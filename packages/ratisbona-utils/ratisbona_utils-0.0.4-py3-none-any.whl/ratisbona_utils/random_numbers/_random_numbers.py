import datetime as dt


def autoseed_16bit() -> int:
    return int(
        dt.datetime.now().microsecond
        * dt.datetime.now().timestamp()
    ) & 0xFFFF_FFFF


def linearCongruentialGenerator(
    modulus_mask: int, coefficient: int, constant: int, seed: int
):
    while True:
        seed = (seed * coefficient + constant) & modulus_mask
        yield seed & modulus_mask


def knuth_mmix(seed):
    return linearCongruentialGenerator(
        0xFFFFFFFF_FFFFFFFF,
        6364136223846793005,
        1442695040888963407,
        seed,
    )

def normalized_generator(generator, modulus_mask: int) -> float:
    while True:
        try:
            yield next(generator) / modulus_mask
        except StopIteration:
            return

def between(lower, upper, normalized_generator):
    while True:
        try:
            yield next(normalized_generator) * (upper - lower) + lower
        except StopIteration:
            return


def lsfr_generator(
    seed: int, polynomal_mask: int
):
    while True:
        seed = (seed >> 1) ^ (-(seed & 1) & polynomal_mask)
        yield seed

def lsfr_B4BCD35C_32Bit(seed: int):
    return lsfr_generator(seed, 0xB4BCD35C)


def int_between(lower, upper, normalized_generator):
    while True:
        try:
            yield int(next(normalized_generator) * (upper - lower + 1) + lower)
        except StopIteration:
            return

