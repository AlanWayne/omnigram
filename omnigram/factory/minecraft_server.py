from functools import lru_cache

from omnigram.minecraft import MinecraftServer


@lru_cache
def get_minecraft_server() -> "MinecraftServer":
    return MinecraftServer()
