
def binary_search_r(r_start, r_end, epsilon, error_measure, step=1, comment='', verbose=False):
    """Binary search to find the minimum number of Trotter steps.

    Args:
        r_start: Starting value for number of steps
        r_end: Ending value for number of steps
        epsilon: Target error threshold
        error_measure: Function to compute error given r
        step: Minimum step size for binary search
        comment: Optional comment for logging
        verbose: Print detailed information

    Returns:
        Minimum number of steps r that achieves error <= epsilon
    """
    print(f'----[{comment}] binary search r (r_start={r_start}, r_end={r_end})----')
    while error_measure(r_end) > epsilon:
        print("the initial r_end is too small, increase it by 10 times.")
        r_end *= 10

    if error_measure(r_start) <= epsilon:
        r = r_start
    else: 
        while r_start < r_end - step: 
            r_mid = int((r_start + r_end) / 2)
            if error_measure(r_mid) > epsilon:
                r_start = r_mid
            else:
                r_end = r_mid
            if verbose: print('r_start:', r_start, '; r_end:', r_end)
        r = r_end
    if verbose: print('r:', r, '; err: ', error_measure(r))
    return r


def normalize(data):
    """Normalize data to sum to 1.

    Args:
        data: List or array of numeric values

    Returns:
        Normalized list where squared values sum to 1
    """
    s = sum(a**2 for a in data)
    return [a**2/s for a in data]



def ob_dt(ob_list, t_list, ord=1):
    """time derivative of observable expectation 

    Args:
        ob_list (_type_): _description_
        t_list (_type_): _description_

    Returns:
        ob_dt_list: _description_
    """
    if ord == 1:
        ob_dt_list = [(ob_list[i + 1] - ob_list[i]) / (t_list[-1]/len(t_list))  for i in range(len(ob_list) - 1)]
    elif ord == 2:
        ob_dt_list = [(ob_list[i + 2] - 2*ob_list[i + 1] + ob_list[i]) / (0.5*t_list[-1]/len(t_list))  for i in range(len(ob_list) - 2)]
    return ob_dt_list
