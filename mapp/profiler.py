from line_profiler import LineProfiler

if "profile" in globals():

    def do_profile():
        def inner(func):
            def profiled_func(*args, **kwargs):
                try:
                    profiler = LineProfiler()
                    profiler.add_function(func)
                    profiler.enable_by_count()
                    return func(*args, **kwargs)
                finally:
                    profiler.print_stats()

            return profiled_func

        return inner


else:

    def do_profile():
        def inner(func):
            def profiled_func(*args, **kwargs):
                return func(*args, **kwargs)

            return profiled_func

        return inner
