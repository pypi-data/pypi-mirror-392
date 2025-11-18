from __future__ import annotations

import itertools
import os
import queue
import socket
import ssl
import threading
import time
from dataclasses import dataclass
from multiprocessing import get_context, connection as mp_connection
from multiprocessing.connection import Connection
from multiprocessing.reduction import send_handle, recv_handle
from typing import Any, Dict, Optional

from . import metrics as metrics_module


@dataclass
class TaskRecord:
    task_id: int
    worker_id: int
    instance: Any
    handle: dict
    handler_timeout: Optional[float]


class ProcessWorker:
    def __init__(self, ctx, worker_id: int, snapshot, shared_resources):
        self.ctx = ctx
        self.worker_id = worker_id
        self.snapshot = snapshot
        self.shared_resources = shared_resources
        self.parent_conn: Connection
        self.child_conn: Connection
        self.parent_conn, self.child_conn = ctx.Pipe()
        self.process = None

    def start(self):
        if self.process and self.process.is_alive():
            return
        self.process = self.ctx.Process(
            target=_worker_main,
            args=(self.worker_id, self.child_conn, self.snapshot, self.shared_resources),
            daemon=True,
        )
        self.process.start()

    def restart(self):
        self.stop()
        self.parent_conn, self.child_conn = self.ctx.Pipe()
        self.start()

    def stop(self):
        if self.process and self.process.is_alive():
            try:
                self.parent_conn.send({'cmd': 'STOP'})
            except Exception:
                pass
            self.process.join(timeout=1)
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1)
        self.process = None

    def send_task(self, task_id: int, conn: socket.socket, addr, server_payload):
        if not self.process or not self.process.is_alive():
            raise RuntimeError('Worker process not available.')
        message = {
            'cmd': 'START',
            'task_id': task_id,
            'addr': addr,
            'server': server_payload,
            'socket_info': {
                'family': conn.family,
                'type': conn.type,
                'proto': conn.proto,
            }
        }
        self.parent_conn.send(message)
        send_handle(self.parent_conn, conn.fileno(), self.process.pid)


class ProcessWorkerPool:
    def __init__(self, config, snapshot_builder, resource_exporter):
        self.config = config
        self.snapshot_builder = snapshot_builder
        self.resource_exporter = resource_exporter
        self.ctx = get_context('spawn')
        self.worker_count = max(1, getattr(config, 'WORKER_PROCESSES', 1))
        self.workers: list[ProcessWorker] = []
        self.available = queue.Queue()
        self.task_seq = itertools.count(1)
        self.tasks: Dict[int, TaskRecord] = {}
        self.lock = threading.Lock()
        self.running = False
        self.listener_thread = None
        self.listener_stop = threading.Event()
        self.conn_map: Dict[Connection, int] = {}

    def start(self):
        if self.running:
            return
        snapshot = self.snapshot_builder()
        shared_resources = self.resource_exporter()
        self.available = queue.Queue()
        self.conn_map = {}
        with self.lock:
            self.tasks.clear()
        self.workers = []
        for worker_id in range(self.worker_count):
            worker = ProcessWorker(self.ctx, worker_id, snapshot, shared_resources)
            worker.start()
            self.workers.append(worker)
            self.available.put(worker_id)
            self.conn_map[worker.parent_conn] = worker_id
        self.running = True
        self.listener_stop.clear()
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()

    def shutdown(self):
        if not self.running:
            return
        self.listener_stop.set()
        if self.listener_thread:
            self.listener_thread.join(timeout=1)
        with self.lock:
            tasks = list(self.tasks.items())
            self.tasks.clear()
        for _, record in tasks:
            self._finalize_instance_handle(record)
        for worker in self.workers:
            worker.stop()
        self.workers = []
        self.conn_map = {}
        self.running = False

    def dispatch_connection(self, instance, conn: socket.socket, addr, handle) -> bool:
        try:
            worker_id = self.available.get_nowait()
        except queue.Empty:
            return False
        worker = self.workers[worker_id]
        task_id = next(self.task_seq)
        server_payload = instance.build_dispatch_payload()
        handler_timeout = getattr(instance, 'handler_timeout', None)
        if handler_timeout is not None and handler_timeout <= 0:
            handler_timeout = None
        record = TaskRecord(
            task_id=task_id,
            worker_id=worker_id,
            instance=instance,
            handle=handle,
            handler_timeout=handler_timeout,
        )
        with self.lock:
            self.tasks[task_id] = record
        try:
            worker.send_task(task_id, conn, addr, server_payload)
        except Exception:
            with self.lock:
                self.tasks.pop(task_id, None)
            self.available.put(worker_id)
            raise
        finally:
            try:
                conn.close()
            except Exception:
                pass
        return True

    def _listen_loop(self):
        while not self.listener_stop.is_set():
            conns = [worker.parent_conn for worker in self.workers if worker.process and worker.process.is_alive()]
            if not conns:
                time.sleep(0.05)
                continue
            ready = []
            try:
                ready = mp_connection.wait(conns, timeout=0.1)
            except Exception:
                continue
            for conn in ready:
                worker_id = self._resolve_worker_id(conn)
                try:
                    message = conn.recv()
                except EOFError:
                    if conn in self.conn_map:
                        self.conn_map.pop(conn, None)
                    self._handle_worker_exit(worker_id)
                    continue
                cmd = message.get('cmd')
                task_id = message.get('task_id')
                if cmd == 'DONE':
                    self._complete_task(task_id)
                elif cmd == 'ERROR':
                    self._complete_task(task_id, error=message.get('error'))
                elif cmd == 'TIMEOUT':
                    self._handle_timeout_notification(task_id)

    def _complete_task(self, task_id, error=None):
        with self.lock:
            record = self.tasks.pop(task_id, None)
        if not record:
            return
        self._finalize_instance_handle(record)
        self.available.put(record.worker_id)

    def _handle_timeout_notification(self, task_id):
        with self.lock:
            record = self.tasks.pop(task_id, None)
        if not record:
            return
        metrics_module.record_timeout('handler')
        self._finalize_instance_handle(record)
        # Worker will exit via watchdog; restart handled in _handle_worker_exit.

    def _handle_worker_exit(self, worker_id):
        if worker_id is None or not self.running:
            return
        pending = []
        with self.lock:
            for task_id, record in list(self.tasks.items()):
                if record.worker_id == worker_id:
                    pending.append(record)
                    self.tasks.pop(task_id, None)
        for record in pending:
            self._finalize_instance_handle(record)
        self._restart_worker(worker_id)
        self.available.put(worker_id)

    def _restart_worker(self, worker_id):
        worker = self.workers[worker_id]
        old_conn = worker.parent_conn
        worker.restart()
        self.conn_map.pop(old_conn, None)
        self.conn_map[worker.parent_conn] = worker_id

    def _finalize_instance_handle(self, record: TaskRecord):
        try:
            record.instance._finalize_handle(record.handle)
        except Exception:
            pass

    def _resolve_worker_id(self, conn):
        worker_id = self.conn_map.get(conn)
        if worker_id is not None:
            return worker_id
        for worker in self.workers:
            if worker.parent_conn == conn:
                return worker.worker_id
        return None


def _worker_main(worker_id, control_conn, snapshot, shared_resources):
    from . import core as core_module
    from . import metrics as metrics_module
    core_module._apply_runtime_snapshot(snapshot)
    core_module._import_global_resources(shared_resources)
    try:
        metrics_resource = core_module.get_global_resource('bbws.metrics')
        metrics_module.attach_store(metrics_resource['store'], metrics_resource.get('lock'))
    except Exception:
        pass
    while True:
        message = control_conn.recv()
        cmd = message.get('cmd')
        if cmd == 'STOP':
            break
        if cmd != 'START':
            continue
        task_id = message['task_id']
        socket_info = message['socket_info']
        addr = message['addr']
        server_payload = message['server']
        try:
            conn = _receive_socket(control_conn, socket_info)
            _serve_connection(conn, addr, server_payload, core_module, control_conn, task_id)
            control_conn.send({'cmd': 'DONE', 'task_id': task_id})
        except Exception as exc:
            control_conn.send({'cmd': 'ERROR', 'task_id': task_id, 'error': str(exc)})


def _receive_socket(control_conn, socket_info):
    handle = recv_handle(control_conn)
    family = socket_info['family']
    sock_type = socket_info['type']
    proto = socket_info['proto']
    dup = socket.socket(family, sock_type, proto, fileno=handle)
    return dup


def _prepare_connection(connection, payload):
    if payload.get('ssl_enabled'):
        return _wrap_ssl_connection(connection, payload)
    keep_alive = payload.get('keep_alive_timeout')
    if keep_alive:
        try:
            connection.settimeout(keep_alive)
        except Exception:
            pass
    return connection


def _wrap_ssl_connection(conn, payload):
    cert_path = payload.get('cert_path')
    key_path = payload.get('key_path')
    handshake_timeout = payload.get('handshake_timeout') or 5
    try:
        conn.settimeout(handshake_timeout)
    except Exception:
        pass
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if cert_path and key_path:
            context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        wrapped = context.wrap_socket(conn, server_side=True)
        keep_alive = payload.get('keep_alive_timeout')
        if keep_alive:
            try:
                wrapped.settimeout(keep_alive)
            except Exception:
                pass
        return wrapped
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        return None


def _serve_connection(connection, addr, server_payload, core_module, control_conn, task_id):
    instance = _ServerContext(server_payload)
    prepared = _prepare_connection(connection, server_payload)
    if prepared is None:
        return
    timeout = server_payload.get('handler_timeout')
    controller = _TimeoutController(prepared, control_conn, task_id, timeout)
    worker_state = _WorkerState(instance, handler_signal=controller)
    try:
        core_module.servlet(prepared, addr, worker_state, server_instance=instance)
    finally:
        controller.stop()
        try:
            prepared.close()
        except Exception:
            pass


class _WorkerState:
    def __init__(self, server_instance, handler_signal=None):
        self._event = threading.Event()
        self._event.set()
        self.request_count = 0
        self.server_instance = server_instance
        self.handler_signal = handler_signal

    def is_set(self):
        return self._event.is_set()

    def set(self):
        self._event.set()

    def clear(self):
        self._event.clear()


class _ServerContext:
    def __init__(self, payload):
        self.__dict__.update(payload)

    def build_dispatch_payload(self):
        return self.__dict__


class _TimeoutController:
    def __init__(self, connection, control_conn, task_id, timeout):
        self.connection = connection
        self.control_conn = control_conn
        self.task_id = task_id
        self.timeout = timeout if timeout and timeout > 0 else None
        self._finished = threading.Event()
        self._thread = None
        self._lock = threading.Lock()

    def start(self):
        if not self.timeout:
            return
        with self._lock:
            if self._thread:
                return
            self._thread = threading.Thread(target=self._watchdog, daemon=True)
            self._thread.start()

    def end(self):
        if not self.timeout:
            return
        self._finished.set()

    def stop(self):
        if not self.timeout:
            return
        self._finished.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=0.05)

    def _watchdog(self):
        if self._finished.wait(self.timeout):
            return
        self._trigger_timeout()

    def _trigger_timeout(self):
        response = (
            b'HTTP/1.1 504 Gateway Timeout\r\n'
            b'Connection: close\r\n'
            b'Content-Length: 0\r\n\r\n'
        )
        try:
            self.connection.sendall(response)
        except Exception:
            pass
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.connection.close()
        except Exception:
            pass
        try:
            self.control_conn.send({'cmd': 'TIMEOUT', 'task_id': self.task_id})
        except Exception:
            pass
        os._exit(1)
