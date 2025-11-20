from collections.abc import Callable


def euler(
    function: Callable[[float], float],
    alpha: float,
    beta: float,
    y0: float,
    n: int,
) -> list:
    """Solve ODE initial value problem using Euler's Method.

    Parameters
    ----------
    function : Callable
        The function.
    alpha : float
        The lower bound.
    beta : float
        The upper bound.
    y0 : float
        The initial value.
    n : int
        The number of partitions.

    Returns
    -------
    list
        A function approximation.
    """
    values = []
    h = (beta - alpha) / n
    x = alpha
    y = y0
    values.append((x, y))

    for _ in range(n):
        y = y + h * function(x, y)
        x = x + h
        values.append((x, y))

    return values


def heun(
    function: Callable[[float], float],
    alpha: float,
    beta: float,
    y0: float,
    n: int,
) -> list:
    """Solve ODE initial value problem using Heun's Method.

    Parameters
    ----------
    function : Callable
        The function.
    alpha : float
        The lower bound.
    beta : float
        The upper bound.
    y0 : float
        The initial value.
    n : int
        The number of partitions.

    Returns
    -------
    list
        A function approximation.
    """
    values = []
    h = (beta - alpha) / n
    x = alpha
    y = y0
    values.append((x, y))

    for _ in range(n):
        y_predictor = y + h * function(x, y)

        y += (h / 2) * (function(x, y) + function(x + h, y_predictor))

        x += h

        values.append((x, y))

    return values


def rk4(
    function: Callable[[float], float],
    alpha: float,
    beta: float,
    y0: float,
    n: int,
) -> list:
    """Solve ODE initial value problem using Runge-Kutta 4.

    Parameters
    ----------
    function : Callable
        The function.
    alpha : float
        The lower bound.
    beta : float
        The upper bound.
    y0 : float
        The initial value.
    n : int
        The number of partitions.

    Returns
    -------
    list
        A function approximation.
    """
    values = []
    h = (beta - alpha) / n
    x = alpha
    y = y0
    values.append((x, y))

    for _ in range(n):
        k1 = function(x, y)
        k2 = function(x + h / 2, y + h * (k1 / 2))
        k3 = function(x + h / 2, y + h * (k2 / 2))
        k4 = function(x + h, y + h * k3)

        y += (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
        x += h

        values.append((x, y))

    return values
