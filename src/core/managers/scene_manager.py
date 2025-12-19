import pygame as pg

from src.scenes.scene import Scene
from src.utils import Logger

class SceneManager:
    
    _scenes: dict[str, Scene]
    _current_scene: Scene | None = None
    _next_scene: str | None = None
    _next_scene_params: dict | None = None

    def __init__(self):
        Logger.info("Initializing SceneManager")
        self._scenes = {}
        
    def register_scene(self, name: str, scene: Scene) -> None:
        self._scenes[name] = scene
        
    def change_scene(self, scene_name: str, **params) -> None:
        if scene_name in self._scenes:
            Logger.info(f"Changing scene to '{scene_name}'")
            self._next_scene = scene_name
            self._next_scene_params = params
        else:
            raise ValueError(f"Scene '{scene_name}' not found")
            
    def update(self, dt: float) -> None:
        # Handle scene transition
        if self._next_scene is not None:
            self._perform_scene_switch()
            
        # Update current scene
        if self._current_scene:
            self._current_scene.update(dt)
            
    def draw(self, screen: pg.Surface) -> None:
        if self._current_scene:
            self._current_scene.draw(screen)
            
    def _perform_scene_switch(self) -> None:
        if self._next_scene is None:
            return
            
        # Exit current scene
        if self._current_scene:
            self._current_scene.exit()
        
        self._current_scene = self._scenes[self._next_scene]
        
        if self._next_scene_params and hasattr(self._current_scene, "set_params"):
            #try:
            self._current_scene.set_params(**self._next_scene_params)
            # except:
            #     Logger.error(f"Scene '{self._next_scene}' set_params does not match given arguments")
        # Enter new scene
        if self._current_scene:
            Logger.info(f"Entering {self._next_scene} scene")
            self._current_scene.enter()
            
        # Clear the transition request
        self._next_scene = None
        self._next_scene_params = None
        