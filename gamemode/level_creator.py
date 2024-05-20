import pygame

class LevelMakerMode():
    def __init__(self, game) -> None:
        self.game = game
        self.screen = game.screen
        self.space = game.space
        self.mode = "move"

    def set_mode(self, mode):
        self.mode = mode

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for body in self.space.bodys:
            body.body.check_selected(mouse_pos)
        
    def event_handler(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        #if left mouse button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN: 

            #this part find and set the item clicked as selected to be able to move it
            if event.button == 1 and len(self.space.bodys) > 0 :
                found = False
                iteration = 0
                #We use a while to avoid being able to select multiple
                #object at the same time and avoid too much call
                items = self.space.bodys
                while not found and iteration < len(items) and items[iteration].body.pygame_shape != None:
                    is_clicked = items[iteration].body.check_clicked(mouse_pos)
                    if is_clicked and not items[iteration].body.is_static:
                        #if actual mode is delete
                        if self.mode == "delete":
                            self.game.remove_item(iteration)
                        #if actual mode is place or move
                        elif self.mode == "move" or self.mode == "place":
                            found = True
                            self.space.bodys[iteration].body.toggle_selected(mouse_pos) #set the item as selected
                            found_item = self.space.bodys.pop(iteration)
                            self.space.bodys.append(found_item) #put the item at the end of the list
                    iteration += 1
                            
        #if left mouse button is released
        elif event.type == pygame.MOUSEBUTTONUP:
            #set the selected item back to not selected 
            if event.button == 1 and len(self.space.bodys) > 0:
                last_item = len(self.space.bodys) - 1
                #if an item is selected
                if self.space.bodys[last_item].body.selected:
                    self.space.bodys[last_item].body.toggle_selected() #unselect the item
            
        #if mousewheel is used
        elif event.type == pygame.MOUSEWHEEL:
            #if an item is selected
            if len(self.space.bodys) > 0:
                last_item = len(self.space.bodys) - 1
                if self.space.bodys[last_item].body.selected:
                    self.space.bodys[last_item].body.rotate_degree(6*event.y) #rotate the item

        #All key detection
        elif event.type == pygame.KEYDOWN:
            pass