from calamari_ocr.proto import BackendParams


def create_backend_from_proto(network_params, restore=None, weights=None, seed=None):
    if network_params.backend.type == BackendParams.TENSORFLOW:
        from calamari_ocr.ocr.backends.tensorflow_backend.tensorflow_backend import TensorflowBackend
        return TensorflowBackend(network_params, restore, weights, seed)
    else:
        raise Exception("Unknown backend type '{}'".format(network_params.backend.type))

