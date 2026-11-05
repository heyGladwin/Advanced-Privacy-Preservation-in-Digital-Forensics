import tenseal as ts


def create_context():

    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )

    context.global_scale = 2**40

    context.generate_galois_keys()

    return context


def encrypt_features(values: list[float]):

    context = create_context()

    encrypted_vector = ts.ckks_vector(
        context,
        values
    )

    return context, encrypted_vector


def perform_encrypted_computation(
    encrypted_vector
):

    scales = [
        1.0,
        1.0,
        0.01,
        1.0,
        1.0,
        1.0
    ]

    encrypted_result = (
        encrypted_vector * scales
    )

    return encrypted_result


def decrypt_result(
    encrypted_result
):

    return encrypted_result.decrypt()