import weakref

import torch
import moodist


weak_group = weakref.WeakValueDictionary()
weak_queue = weakref.WeakKeyDictionary()


class Name(str):
    pass


def prepare_custom(group, shape, dtype, input=None, output=None):
    assert isinstance(dtype, torch.dtype)
    shape = tuple(shape)
    for x in shape:
        assert isinstance(x, int)

    name = Name(group.moodist_name() + ".{prepare_custom_queue}")
    if name not in weak_group:
        print("creating a new queue for prepare_custom")
        weak_group[name] = group
        weak_queue[name] = moodist.Queue(group, range(group.size()), name=name)
    queue = weak_queue.get(name)
    assert isinstance(queue, moodist.Queue)

    def check(l):
        assert isinstance(l, (tuple, list))
        for x in l:
            assert isinstance(x, dict)
            for n in ("offset", "shape"):
                assert n in x, "%s is missing for an input or output" % n
                v = x[n]
                assert isinstance(v, (tuple, list)), "%s must be a tuple or list" % n
                assert len(v) == len(
                    shape
                ), "expected %s with %d dimensions, but got %d" % (
                    n,
                    len(shape),
                    len(v),
                )
                for z in v:
                    assert isinstance(z, int)
        return tuple((tuple(x["offset"]), tuple(x["shape"])) for x in l)

    if input is not None:
        input = check(input)
    if output is not None:
        output = check(output)

    assert queue.empty()
    group.barrier()

    info = (group.rank(), shape, dtype, input, output)
    queue.put_object(info)

    all_inputs = []
    all_outputs = []

    for _ in range(group.size()):
        source_rank, nshape, ndtype, ninput, noutput = queue.get_object()
        assert (
            nshape == shape
        ), "moodist.prepare_custom: Ranks specified different shapes"
        assert (
            ndtype == dtype
        ), "moodist.prepare_custom: Ranks specified different dtypes"

        if ninput is not None:
            for o, s in ninput:
                all_inputs.append((source_rank, o, s))
        if noutput is not None:
            for o, s in noutput:
                all_outputs.append((source_rank, o, s))

    assert queue.empty()
    group.barrier()

    print("inputs: %s" % all_inputs)
    print("outputs: %s" % all_outputs)

    return group.prepare_custom_full(shape, dtype, all_inputs, all_outputs)
