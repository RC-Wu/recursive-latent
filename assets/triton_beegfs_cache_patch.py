"""Runtime patch for Triton cache writes on BeEGFS.

Triton uses os.replace from a temporary path into the cache path. On this A100
BeEGFS mount that can raise Errno 16 for generated shared objects. For the
single-process diagnostics in this project, direct final-path writes are an
acceptable fallback because the cache directory is run-scoped.
"""

from __future__ import annotations

import errno
import os
import shutil
import uuid


def apply_triton_beegfs_cache_patch() -> bool:
    try:
        from triton.runtime.cache import FileCacheManager
    except Exception:
        return False

    if getattr(FileCacheManager, "_rgg_beegfs_patch", False):
        return True

    original_put = FileCacheManager.put

    def patched_put(self, data, filename, binary=True):
        try:
            return original_put(self, data, filename, binary=binary)
        except OSError as exc:
            if exc.errno != errno.EBUSY:
                raise
            if not self.cache_dir:
                raise
            payload_is_bytes = isinstance(data, bytes)
            if not payload_is_bytes:
                data = str(data)
            filepath = self._make_path(filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            tmp_path = filepath + f".direct_tmp_{os.getpid()}_{uuid.uuid4()}"
            mode = "wb" if payload_is_bytes else "w"
            with open(tmp_path, mode) as handle:
                handle.write(data)
            try:
                os.rename(tmp_path, filepath)
            except OSError as rename_exc:
                if rename_exc.errno != errno.EBUSY:
                    raise
                shutil.copyfile(tmp_path, filepath)
                os.unlink(tmp_path)
            return filepath

    FileCacheManager.put = patched_put
    FileCacheManager._rgg_beegfs_patch = True
    return True
