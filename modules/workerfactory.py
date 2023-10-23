from .smspool import smspool
from .spamotp import spamotp

workertype = {
        "smspool" : smspool,
        "spamotp" : spamotp,
}

def workerfactory(wktype = "smspool"):
    try:
        return workertype[wktype]
    except:
        print("Not found a woker", wktype)
        return None


def gen_worker_desc():
    output = {}
    for k in workertype:
        wker = workerfactory(k)(k, {})
        output[k] = wker.get_description()
    print(output)
    return output


if __name__ == '__main__':
    gen_worker_desc()
