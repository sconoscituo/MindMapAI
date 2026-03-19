import threading


class ServiceFactory:
    _instances = {}
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, service_class, *args, **kwargs):
        if service_class not in cls._instances:
            with cls._lock:
                if service_class not in cls._instances:
                    cls._instances[service_class] = service_class(*args, **kwargs)
        return cls._instances[service_class]
