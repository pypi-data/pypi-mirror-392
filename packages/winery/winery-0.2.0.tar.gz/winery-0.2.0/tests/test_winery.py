import pytest
import tempfile
from pathlib import Path


def test_temppath_add(winery_instance, conf):
    with tempfile.TemporaryDirectory() as temp_dir:
        win1 = winery_instance(template_path=temp_dir, local_time=conf["local_time"])
        assert win1.template_path == Path(temp_dir)
        win2 = winery_instance(
            template_path=str(temp_dir), local_time=conf["local_time"]
        )
        assert win2.template_path == Path(temp_dir)
        with pytest.raises(ValueError):
            winery_instance(
                template_path=str("someinvalidpath"), local_time=conf["local_time"]
            )
