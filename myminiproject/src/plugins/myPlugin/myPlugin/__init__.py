"""
This is where the implementation of the plugin code goes.
The new_plugin-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('new_plugin')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class new_plugin(PluginBase):
  def main(self):
    
    active_node = self.active_node
    core = self.core
    META = self.META
    logger = self.logger
    logger.debug('path: {0}'.format(core.get_path(active_node)))
    logger.info('name: {0}'.format(core.get_attribute(active_node, 'name')))
    logger.warn('pos : {0}'.format(core.get_registry(active_node, 'position')))
    logger.error('guid: {0}'.format(core.get_guid(active_node)))
       
    parent_node = core.get_parent(core.get_parent(core.get_parent(active_node)))
    nodesList = core.load_sub_tree(parent_node)
    nodes = {}
    for node in nodesList:
      nodes[core.get_path(node)] = node
    self.nodes = nodes
      
    # Iterate over all states from node name
    game_list = []
  
    for path in nodes:
      # Check if node is an instane of GameState META
      # Store Example and Other as the two different states 
      node = nodes[path]    

      if (core.is_instance_of(node, META['GameState'])):
        logger.info(core.get_attribute(node, 'name'))
        game_state = {"path": " " ,"name": "none", "currentMove": {"color": "none", "row": 0 , "column": 0}, "currentPlayer":"none", "board" : []}
        game_state["path"] = path   
        # get game state name:
        name_game_state = core.get_attribute(node, 'name')
        game_state["name"] = name_game_state
        # Get all chlidren nodes from the GameState
        childrenPaths = core.get_children_paths(node)
        
        # Get all pointers paths for currentMove and currentPlayer ptrss
        pointer_names = core.get_pointer_names(node)
        # current piece
        currentMove_pointer_path = core.get_pointer_path(node,"currentMove")
        piece = nodes[currentMove_pointer_path]
        currentMove_piece = core.get_attribute(piece, "color")
        # extract the parent tile that the piece belings to
        tile_node = core.get_parent(piece)        
        tile_node_x = core.get_attribute(tile_node, "row")
        tile_node_y = core.get_attribute(tile_node, "column")
        
        #logger.info('currentMove:[color:{0}, row:{1}, column:{2}]'.format(currentMove_piece,tile_node_x, tile_node_y))
        game_state["currentMove"]["color"] = currentMove_piece
        game_state["currentMove"]["row"] = tile_node_x
        game_state["currentMove"]["column"] = tile_node_y
        # extarct current player  
        currentPlayer_pointer = core.get_pointer_path(node,"currentPlayer")
        logger.info(currentPlayer_pointer)
        current_player_node = nodes[currentPlayer_pointer]
        cuurentPlayer_Color = core.get_attribute(current_player_node, "color")
        game_state["currentPlayer"] = cuurentPlayer_Color
        
        # Define Board
        board = [[None for _ in range(8)] for _ in range(8)]
        
        for child in childrenPaths:
          child_node_name = core.get_attribute(nodes[child], 'name')      
          # Check if child node is board
          if child_node_name == "Board":
          
            BoardChildrenPaths = core.get_children_paths(nodes[child])  
            # Extract all children of board
            for board_child in BoardChildrenPaths:
              path_node = nodes[board_child]
             
              # Define tile dictionary 
              tile = {"path": " ", "color": " ", "flip" : []}     

              if core.is_instance_of(path_node, META["Tile"]):
                  tile_node = core.get_attribute(path_node, 'name')  
                  row = core.get_attribute(path_node, 'row')    
                  column = core.get_attribute(path_node, 'column') 
                  
                  # Extract all peices associated with each tile node
                  TileChildrenPaths = core.get_children_paths(path_node)             
                  if len(TileChildrenPaths) > 0:
                    childpath = TileChildrenPaths[0] 
                    color_child = core.get_attribute(nodes[childpath],'color')
                    tile["color"] = color_child
                    tile["path"] = childpath
                    for path2 in nodes:
                      if core.is_instance_of(nodes[path2], META["mightFlip"]):
                        source_tile_path = core.get_pointer_path(nodes[path2], "src")
                        dist_tile_path = core.get_pointer_path(nodes[path2], "dst")
                        
                        src_tile = core.get_parent(nodes[source_tile_path])
                        dst_tile = core.get_parent(nodes[dist_tile_path])
                        
                        srcInfo = {"column": core.get_attribute(src_tile, "column"), "row": core.get_attribute(src_tile, "row")}
                        dstInfo = {"column": core.get_attribute(dst_tile, "column"), "row": core.get_attribute(dst_tile, "row")}
                        
                        if path_node == src_tile:
                          tile["flip"].append(dstInfo)
                          
                  board[row][column] = tile

                      
        # append board to the game_state
        game_state["board"] = board
        
        # append game stae to the list of states
        game_list.append(game_state)

        # As the ticatactoegame prototype already has everything setup we do not need
        # to do anything further.
        self.util.save(self.root_node, self.commit_hash, 'master', 'created a new game object which should be renamed')
        self.create_message(active_node, core.get_path(new_game))

    ## Visualizing the game states that exist
    # for i in range(len(game_list)):
    #   state_string = """[
    #   path : {}
    #   name: {}
    #   currentPlayer: {}
    #   currentMove: color:{}, row: {}, column:{}
    #   """.format(game_list[i]["path"],game_list[i]["name"],game_list[i]["currentPlayer"], game_list[i]["currentMove"]["color"], game_list[i]["currentMove"]["row"], game_list[i]["currentMove"]["column"])     
    #   boardstring = "board:\n["
    #   for j in range(8):
    #     rowstring = "["
    #     for k in range(8):
    #       rowstring += "[color: {}, flip{}]".format(game_list[i]["board"][j][k]["color"],game_list[i]["board"][j][k]["flip"])
    #     rowstring += "]"
    #     boardstring += rowstring
    #     boardstring += "\n"
    #   boardstring += "]\n]"
    #   state_string += boardstring
    #   logger.info(state_string)
        
        
          

 


                      
            



          





    
   
          
        
        
      
      
      
    
    
