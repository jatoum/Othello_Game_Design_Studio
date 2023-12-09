"""
This is where the implementation of the plugin code goes.
The flipping-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('flipping')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class flipping(PluginBase):
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
    i = 0
    j = -1  
    for path in nodes:
      # Check if node is an instane of GameState META
      # Store Example and Other as the two different states 
      node = nodes[path]    

      if (core.is_instance_of(node, META['GameState'])):
        j = j + 1
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
        i = i + 1
        
    # Check if piece canbe placed on tile   
    self.game_state_list = game_list      
    can_place = self.can_be_placed()
    logger.info("Can be placed: {}".format(self.can_be_placed()))
    
    # Update the next game state based on new tile placement
    self.create_next_game_state(can_place, j)
   
  
  
  # Function to check if piece can be placed on current tile     
  def can_be_placed(self):
    self.pieces_flipped = []
    can_be_placed = False
    active_node = self.active_node
    core = self.core
    META = self.META
    logger = self.logger
    game_state_list = self.game_state_list
    nodes = self.nodes
    board_node = core.get_parent(active_node)
    game_state_node = core.get_parent(board_node)
    current_board_path = core.get_path(game_state_node)
    nextMove = [
      (-1,-1),
      (-1,0),
      (0,-1),
      (0,0),
      (0,1),
      (1,0),
      (1,1)
    ]
    # get peices that can be flipped
    piece_flipped = []
    oppColor = {"black": "white", "white":"black"}
    for i in range(len(game_state_list)):
      
      # Extract the board with the game state path from the create game list
      if (game_state_list[i]["path"] == str(current_board_path)):
        current_board = game_state_list[i]["board"]
        node = nodes[current_board_path]
        core.CONSTANTS
        # current piece
        currentMove_pointer_path = core.get_pointer_path(node,"currentMove")
        piece = nodes[currentMove_pointer_path]
        current_move_color= core.get_attribute(piece, "color")
        next_move_color = oppColor[current_move_color]
        # extract the current tile position     
        move_x = core.get_attribute(active_node, "row")
        move_y = core.get_attribute(active_node, "column")
            
        # First check if there is a piece on the current tile
        is_tile_occupied =  current_board[move_x][move_y]["color"]
        #check if the tile is empty or not
        if (is_tile_occupied == " "):
          # Check if the next tile is of opposing color of the currentMove color
          for move in nextMove:
            currentMove_x = move_x +  move[0]
            currentMove_y = move_y + move[1]
            # Check if we are at th ebounday of the board
            if (0 <= currentMove_x < 8 )and(0 <= currentMove_y < 8):
                  # Get the color of the piece   
                  piece_color =  current_board[currentMove_x][currentMove_y]["color"]
                  if(piece_color == current_move_color): 
                    piece_flipped.append((currentMove_x, currentMove_y))
                    while((0 <= currentMove_x < 7 )and (0 <= currentMove_y < 7)):
                      currentMove_x += move[0]
                      currentMove_y += move[1]
                      piece_color = current_board[currentMove_x][currentMove_y]["color"]
                      piece_flipped.append((currentMove_x, currentMove_y))
                      if (piece_color == next_move_color):
                        logger.info("Valid Move")
                        [self.pieces_flipped.append(x) for x in piece_flipped]
                        can_be_placed = True
                      piece_flipped = []                    
        else:
          #logger.error("In-Valid Move: Tile is occupied")
          can_be_placed = False
    return can_be_placed
        
  # Function to update pieces color if can be placed is True      
  def update_pieces_color(self, new_color):
    core = self.core
    META = self.META
    logger = self.logger
    tile_nodes = self.tile_nodes
    flipped_pieces = self.pieces_flipped
       
    for x, y in flipped_pieces:
      for tile in tile_nodes:
          x_new = core.get_attribute(tile, "row")
          y_new = core.get_attribute(tile, "column")
          if (x == x_new and y == y_new):
            piece = core.load_children(tile)[0]

            core.set_attribute(piece, "color", new_color)
            logger.info("color of flipped pieces: {}".format(core.get_attribute(piece, "color")))  
    return
            
  # Function to update new game state nodes based on the piece placement  
  def create_next_game_state(self, valid, j):
    core = self.core
    META = self.META
    logger = self.logger
    nodes = self.nodes 
    is_valid = self.can_be_placed()

    if (is_valid):
      
      active_node = self.active_node
      row = core.get_attribute(active_node, 'row')
      col = core.get_attribute(active_node, 'column')
      # Gett path of active node
      active_node_path = core.get_path(active_node)
      
      board_node = core.get_parent(active_node)
      game_state_node = core.get_parent(board_node)
      current_board_path = core.get_path(game_state_node)
      oppColor = {"black": "white", "white":"black"}

      # Current piece and player color
      node = nodes[current_board_path]
      currentMove_pointer_path = core.get_pointer_path(node,"currentMove")
      current_player_path = core.get_pointer_path(node,"currentPlayer")
      piece = nodes[currentMove_pointer_path]
      current_move_color= core.get_attribute(piece, "color")
      next_player_color = oppColor[current_move_color]
      logger.info("current player color: {}".format(current_move_color))
      
      # Copy current game state node to new game state node:
      self.new_game_state_node = core.copy_node(game_state_node, core.get_parent(game_state_node))
      new_game_state_node = self.new_game_state_node
      children_node = core.load_children(new_game_state_node)
      
      nodesList = core.load_sub_tree(new_game_state_node)  
      nodes = {}
      for node in nodesList:
        nodes[core.get_path(node)] = node
      self.new_nodes = nodes 
      
      # Check if new gane state is an instance of Meta GameState: 
      if (core.is_instance_of(new_game_state_node, META['GameState'])):    
        # Set new game state name  
        core.set_attribute(new_game_state_node, "name","OthelloGmaeState{}".format(j))
        for child in children_node:
          # Set pointer to the next player of opposing color
          if (core.is_instance_of(child, META['Player'])):
            color_child = core.get_attribute(child, "color")
            logger.info("color_child: {}".format(color_child))
            if(next_player_color == color_child):
                core.set_pointer(new_game_state_node, 'currentPlayer',child)
                logger.info("color set of next player: {}".format(color_child))
                
        for child in children_node:
          # Get board isnatnce
          if (core.is_instance_of(child, META['Board'])):
            new_board_node = child
            # Load the tiles on board
            self.tile_nodes = core.load_children(new_board_node)
            tile_nodes = self.tile_nodes
            for child2 in tile_nodes:
              # Get active_node check to be placed
              row_new = core.get_attribute(child2, "row")
              col_new = core.get_attribute(child2, "column")
              if(row_new == row and col_new == col):
                #Create new piece after checking that the tile matches the cuurent tile
                new_piece_node = core.create_node({"parent": child2 ,"base": META["Piece"]})
                core.set_pointer(new_game_state_node, 'currentMove', new_piece_node)
                core.set_attribute(new_piece_node, "color", next_player_color)
                logger.info(core.get_attribute(new_piece_node , "name"))
                # Update color of pieces after placement of new piece
                self.update_pieces_color(next_player_color)
        logger.info("here")
        self.util.save(self.new_game_state_node, self.commit_hash, self.branch_name)
    else:
      logger.error("In-Valid move, board hasn't changed")
      self.create_message(self.active_node, "This is an in-valid move")
        
      
  

                  
      
  

                  
