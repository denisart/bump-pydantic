import pytest
from libcst.codemod import CodemodTest

from bump_pydantic.codemods.replace_config import ReplaceConfigCodemod


class TestReplaceConfigCommand(CodemodTest):
    TRANSFORM = ReplaceConfigCodemod

    maxDiff = None

    def test_config(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(allow_arbitrary_types=True)
        """
        self.assertCodemod(before, after)

    def test_noop_config(self) -> None:
        code = """
        from pydantic import BaseModel

        class Potato:
            class Config:
                allow_mutation = True
        """
        self.assertCodemod(code, code)

    @pytest.mark.xfail(reason="Not implemented yet")
    def test_noop_config_with_bases(self) -> None:
        code = """
        from potato import RandomBase

        class Potato(RandomBase):
            class Config:
                allow_mutation = True
        """
        self.assertCodemod(code, code)

    def test_global_config_class(self) -> None:
        code = """
        from pydantic import BaseModel as Potato

        class Config:
            allow_arbitrary_types = True
        """
        self.assertCodemod(code, code)

    def test_reset_config_args(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True

        potato = Potato()

        class Potato2(BaseModel):
            class Config:
                allow_mutation = True
        """
        after = """
        from pydantic import ConfigDict, BaseModel

        class Potato(BaseModel):
            model_config = ConfigDict(allow_arbitrary_types=True)

        potato = Potato()

        class Potato2(BaseModel):
            model_config = ConfigDict(allow_mutation=True)
        """
        self.assertCodemod(before, after)

    def test_config_with_non_assign(self) -> None:
        before = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            class Config:
                allow_arbitrary_types = True

                def __init__(self):
                    self.allow_mutation = True
        """
        after = """
        from pydantic import BaseModel

        class Potato(BaseModel):
            # TODO[pydantic]: We couldn't refactor this class, please create the `model_config` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            class Config:
                allow_arbitrary_types = True

                def __init__(self):
                    self.allow_mutation = True
        """
        self.assertCodemod(before, after)

    def test_inherited_config(self) -> None:
        before = """
        from pydantic import BaseModel

        from potato import SuperConfig

        class Potato(BaseModel):
            class Config(SuperConfig):
                allow_arbitrary_types = True
        """
        after = """
        from pydantic import BaseModel

        from potato import SuperConfig

        class Potato(BaseModel):
            # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
            # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
            class Config(SuperConfig):
                allow_arbitrary_types = True
        """
        self.assertCodemod(before, after)