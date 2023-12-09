"""
This is where the implementation of the plugin code goes.
The counting_pieces-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('counting_pieces')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class counting_pieces(PluginBase):
  def main(self):
    active_node = self.active_node
    core = self.core
    logger = self.logger
    META = self.META
    logger.debug('path: {0}'.format(core.get_path(active_node)))
    logger.info('name: {0}'.format(core.get_attribute(active_node, 'name')))
    logger.warn('pos : {0}'.format(core.get_registry(active_node, 'position')))
    logger.error('guid: {0}'.format(core.get_guid(active_node)))
    
    nodesList = core.load_sub_tree(active_node)
    nodes = {}
    for node in nodesList:
      nodes[core.get_path(node)] = node
    self.nodes = nodes   
    # Iterate over all states from node name
    '''
    for path in nodes:
      # Check if node is an instane of GameState META
      # Store Example and Other as the two different states 
      node = nodes[path]  
    '''
    if (core.is_instance_of(active_node, META['GameFolder'])): 
      # Get current game state path      
      current_game_state_path = self.current_game_state_path = core.get_pointer_path(active_node,"current game")
      current_game_state_node = core.load_by_path(self.root_node, self.current_game_state_path)
      self.current_game_state_node = current_game_state_node
      '''
      if (core.is_instance_of(node, META['GameState'])):
        logger.info(core.get_attribute(node, 'name'))
        game_state = {"path": " " ,"name": "none", "currentMove": {"color": "none", "row": 0 , "column": 0}, "currentPlayer":"none", "board" : []}
        game_state["path"] = path   
        # get game state name:
        name_game_state = core.get_attribute(node, 'name')
        game_state["name"] = name_game_state
        # Get all chlidren nodes from the GameState
        childrenPaths = core.get_children_paths(node)
      '''
      game_state = {"path": " " ,"name": "none", "currentMove": {"color": "none", "row": 0 , "column": 0}, "currentPlayer":"none", "board" : []}
      game_state["path"] = current_game_state_path   
      # get game state name:
      name_game_state = core.get_attribute(current_game_state_node, 'name')
      game_state["name"] = name_game_state
      childrenPaths = core.get_children_paths(current_game_state_node)
      # current piece
      currentMove_pointer_path = core.get_pointer_path(current_game_state_node,"currentMove")
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
      currentPlayer_pointer = core.get_pointer_path(current_game_state_node,"currentPlayer")
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
      self.game_state = game_state  
      # Count number of balck and white pieces on board
      self.counting_pieces()
      # Auto function 
      #self.auto()
      # Highlight valid tiles
      #self.highlight()
      # Undo function
      #self.undo()
  
  # Function to check if piece can be placed on current tile     
  def can_be_placed(self, tile):
    self.pieces_flipped = []
    can_be_placed = False
    core = self.core
    META = self.META
    logger = self.logger
    game_state = self.game_state 
    nodes = self.nodes
     
    active_node = tile
    self.current_tile_nodes = []
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
    self.oppColor = {"black": "white", "white":"black"}
    # Extract the board with the game state path from the create game list
    if (game_state["path"] == str(current_board_path)):
      current_board = game_state["board"]
      node = core.load_by_path(self.root_node,current_board_path)
      # current piece
      currentMove_pointer_path = core.get_pointer_path(node,"currentMove")
      piece = core.load_by_path(self.root_node,currentMove_pointer_path)
      current_move_color= core.get_attribute(piece, "color")
      self.next_move_color = self.oppColor[current_move_color]
      # extract the current tile position     
      move_x = core.get_attribute(active_node, "row")
      move_y = core.get_attribute(active_node, "column")
            
      # First check if there is a piece on the current tile
      is_tile_occupied = current_board[move_x][move_y]["color"]
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
                  if (piece_color == self.next_move_color):
                    logger.info("Valid Move")
                    [self.pieces_flipped.append(x) for x in piece_flipped]
                    can_be_placed = True
                    self.current_tile_nodes.append(active_node)
                    # change attribute valid to valid for the tile that meets all coidtions to represent highlight
                    core.set_attribute(active_node, "valid", True)
                  piece_flipped = []                    
      else:
        #logger.error("In-Valid Move: Tile is occupied")
        can_be_placed = False
    return can_be_placed, self.current_tile_nodes, self.pieces_flipped

  # Function to highlight the tile
  def highlight(self):
    valid_tile_node=[]
    valid_tiles = []
    valid_flip=[]
    core = self.core
    META = self.META
    logger = self.logger
    nodes = self.nodes
    current_game_state = self.current_game_state_node 
    childrenPaths = core.get_children_paths(current_game_state)
    for child in childrenPaths:
      if(core.is_instance_of(core.load_by_path(self.root_node,child), META['Board'])):
        board_node = core.load_by_path(self.root_node,child)
        current_board_path = child
        # Get the children of the board "Tiles"
        tilechildrenPaths = core.get_children_paths(board_node)
        for tile_path in tilechildrenPaths:
          if(len(tilechildrenPaths) > 0 ):
            tile_node = core.load_by_path(self.root_node,tile_path)
            if(core.is_instance_of(tile_node, META['Tile'])):
              valid, current_tiles, flip = self.can_be_placed(tile_node)                       
              if(valid):
                valid_tile_node.append(tile_node)
                valid_flip.append(flip)
    return valid_tile_node, valid_flip
  
  def auto_generated_new_state(self, auto_tile, auto_flip):
    core = self.core
    logger = self.logger
    META = self.META
    
    # Get row an dcolumn of auto_tile
    row = core.get_attribute(auto_tile, 'row')
    col = core.get_attribute(auto_tile, 'column')
    
    # Copy current node and save it as previous state
    current_game_state = self.current_game_state_node 
    game_folder_node = core.get_parent(current_game_state)
    new_game_state_node = core.copy_node(current_game_state, game_folder_node)
    self.new_game_state_node = new_game_state_node
    core.set_pointer(new_game_state_node,'Previous State',current_game_state) #Move the previous pointer to previous gamestate ("current")
    core.set_pointer(game_folder_node,'current game',new_game_state_node)  # Move current pointer to the current gamestate that is the one created  
    core.set_pointer(current_game_state, 'Next State', new_game_state_node) 
    # Update the new game state
    children_node = core.load_children(new_game_state_node)
    nodesList = core.load_sub_tree(new_game_state_node)  
    nodes = {}
    for node in nodesList:
      nodes[core.get_path(node)] = node
    self.new_nodes = nodes     
    # Check if new gane state is an instance of Meta GameState: 
    if (core.is_instance_of(new_game_state_node, META['GameState'])):
      # Set new game state name
      game_state_name = core.get_attribute(current_game_state, "name")
      if (len(game_state_name.split("_")) < 2 ):
         new_indx = 1
      else:
        new_indx = game_state_name.split("_")[1] + 1        
      core.set_attribute(new_game_state_node, "name",f"{game_state_name}_{new_indx}")
      for child in children_node:
        # Set pointer to the next player of opposing color
        if (core.is_instance_of(child, META['Player'])):
          color_child = core.get_attribute(child, "color")
          if(self.next_move_color != color_child):
            core.set_pointer(new_game_state_node, 'currentPlayer',child)
      for child in children_node:
        # Get board isnatnce
        if (core.is_instance_of(child, META['Board'])):
          new_board_node = child
          # Load the tiles on board
          self.tile_nodes = core.load_children(new_board_node)
          tile_nodes = self.tile_nodes
          for tile in tile_nodes:
            # Get active_node check to be placed
            row_new = core.get_attribute(tile, "row")
            col_new = core.get_attribute(tile, "column")
            if(row_new == row and col_new == col):
              #Create new piece after checking that the tile matches the cuurent tile
              new_piece_node = core.create_node({"parent": tile ,"base": META["Piece"]})
              core.set_pointer(new_game_state_node, 'currentMove', new_piece_node)
              core.set_attribute(new_piece_node, "color", self.next_move_color)
              logger.info(core.get_attribute(new_piece_node , "name"))           
            elif (row_new, col_new) in auto_flip:
              piece_path = core.get_children_paths(tile)[0]
              # change the pieces to be flipped to the next color
              logger.info(self.next_move_color)
              core.set_attribute(core.load_by_path(self.root_node, piece_path), 'color', self.next_move_color)
    self.util.save(self.root_node, self.commit_hash, self.branch_name)
  
  def auto(self):
    from random import randrange
    active_node = self.current_game_state_node
    core = self.core
    logger = self.logger
    valid_tiles=[]
    self.namespace = None
    META = self.META
    # Extract viable tiles or form highlighted tiles
    possible_moves,to_flip_pieces=self.highlight()
    # Choose a random tile
    if(len(possible_moves) < 1):
      logger.info("No valid moves to be performed by auto")
    else:
      random_index = randrange(len(possible_moves))
      # Make new state from auto
      self.auto_generated_new_state(possible_moves[random_index],to_flip_pieces[random_index])
    
    
  # Defining Undo plugin
  # How do we bind it to an event:: Visualizer
  def undo(self): 
    core = self.core
    META = self.META
    logger = self.logger
    active_node=self.active_node
        
    nodesList = core.load_sub_tree(active_node)
    nodes = {}
    for node in nodesList:
      nodes[core.get_path(node)] = node
         
    # Extract the current game to delete and extract the node pointing to the previous state   
    current_game_state_node_path = core.get_pointer_path(active_node,"current game") 
    current_game_state_node = nodes[current_game_state_node_path]
    logger.info(core.get_attribute(current_game_state_node, "name"))
    # Change the self.current_game_state to the  previous game state
    previous_game_state_path_retrieved = core.get_pointer_path(current_game_state_node, "Previous State")
    previous_game_state_retrieved =core.load_by_path(self.root_node, previous_game_state_path_retrieved)
    # Set the current game pointer to the retrieved previous game state so the game folder will point at it when main plugin is called
    core.set_pointer(active_node,"current game", previous_game_state_retrieved)
    # Delete the previous node
    logger.info("here")
    core.delete_node(current_game_state_node)
    # save new game state
    self.util.save(self.root_node,self.commit_hash,self.branch_name)
 
 # Defining counting pieces plugin
  # How do we return balck and white counts?
  def counting_pieces(self):
    core = self.core
    META = self.META
    logger = self.logger
    nodes = self.nodes
    black_count = 0
    white_count = 0
    
    current_game_state = self.current_game_state_node 
    childrenPaths = core.get_children_paths(current_game_state)
    for child in childrenPaths:
      if(core.is_instance_of(nodes[child], META["Board"])):
        board_node = nodes[child]
        current_board_path = child     
        # Get the children of the board "Tiles"
        tilechildrenPaths = core.get_children_paths(board_node)         
        for tile_path in tilechildrenPaths:
            tile_node = nodes[tile_path]
            # Get pieces if any on tile, xtract all peices associated with each tile node
            TileChildrenPaths = core.get_children_paths(tile_node)             
            if len(TileChildrenPaths) > 0:
              piece_path = TileChildrenPaths[0] 
              color_piece = core.get_attribute(nodes[piece_path],'color')
              if color_piece == "black":
                   black_count = black_count + 1
              else:
                   white_count = white_count + 1
      logger.info(f"white_count: {white_count}")   
      logger.info(f"black_count: {black_count}") 
    return black_count, white_count  
 
