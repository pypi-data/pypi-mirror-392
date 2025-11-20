# Home

<p align="center">
    <a href="https://github.com/durandtibo/minrecord/actions">
        <img alt="CI" src="https://github.com/durandtibo/minrecord/workflows/CI/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/minrecord/actions">
        <img alt="Nightly Tests" src="https://github.com/durandtibo/minrecord/workflows/Nightly%20Tests/badge.svg">
    </a>
    <a href="https://github.com/durandtibo/minrecord/actions">
        <img alt="Nightly Package Tests" src="https://github.com/durandtibo/minrecord/workflows/Nightly%20Package%20Tests/badge.svg">
    </a>
    <a href="https://codecov.io/gh/durandtibo/minrecord">
        <img alt="Codecov" src="https://codecov.io/gh/durandtibo/minrecord/branch/main/graph/badge.svg">
    </a>
    <br/>
    <a href="https://durandtibo.github.io/minrecord/">
        <img alt="Documentation" src="https://github.com/durandtibo/minrecord/workflows/Documentation%20(stable)/badge.svg">
    </a>
    <a href="https://durandtibo.github.io/minrecord/">
        <img alt="Documentation" src="https://github.com/durandtibo/minrecord/workflows/Documentation%20(unstable)/badge.svg">
    </a>
    <br/>
    <a href="https://github.com/psf/black">
        <img  alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/%20style-google-3666d6.svg">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff" style="max-width:100%;">
    </a>
    <a href="https://github.com/guilatrova/tryceratops">
        <img  alt="Doc style: google" src="https://img.shields.io/badge/try%2Fexcept%20style-tryceratops%20%F0%9F%A6%96%E2%9C%A8-black">
    </a>
    <br/>
    <a href="https://pypi.org/project/minrecord/">
        <img alt="PYPI version" src="https://img.shields.io/pypi/v/minrecord">
    </a>
    <a href="https://pypi.org/project/minrecord/">
        <img alt="Python" src="https://img.shields.io/pypi/pyversions/minrecord.svg">
    </a>
    <a href="https://opensource.org/licenses/BSD-3-Clause">
        <img alt="BSD-3-Clause" src="https://img.shields.io/pypi/l/minrecord">
    </a>
    <br/>
    <a href="https://pepy.tech/project/minrecord">
        <img  alt="Downloads" src="https://static.pepy.tech/badge/minrecord">
    </a>
    <a href="https://pepy.tech/project/minrecord">
        <img  alt="Monthly downloads" src="https://static.pepy.tech/badge/minrecord/month">
    </a>
    <br/>
</p>

## Overview

`minrecord` is a minimalist Python library to record values in a ML workflow.
In particular, it provides functionalities to track the best value, or the most recent values by
storing a limiting number of values.
It is possible to customize the library e.g. it is possible to define a new logic to track the best
value.
Below is an example to show how to track the best scalar value when the best value is the maximum
value and when the best value is the minimum value.

```pycon

>>> from minrecord import MaxScalarRecord, MinScalarRecord
>>> record_max = MaxScalarRecord("accuracy")
>>> record_max.update([(0, 42), (None, 45), (2, 46)])
>>> record_max.add_value(40)
>>> record_max.get_best_value()
46
>>> record_min = MinScalarRecord("loss")
>>> record_min.update([(0, 42), (None, 45), (2, 46)])
>>> record_min.add_value(50)
>>> record_min.get_best_value()
42

```

## API stability

:warning: While `minrecord` is in development stage, no API is guaranteed to be stable from one
release to the next. In fact, it is very likely that the API will change multiple times before a
stable 1.0.0 release. In practice, this means that upgrading `minrecord` to a new version will
possibly break any code that was using the old version of `minrecord`.

## License

`minrecord` is licensed under BSD 3-Clause "New" or "Revised" license available
in [LICENSE](https://github.com/durandtibo/minrecord/blob/main/LICENSE) file.
