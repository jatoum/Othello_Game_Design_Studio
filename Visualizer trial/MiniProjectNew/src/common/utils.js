define(['./constants'], function (CONSTANTS) {
    return {
        getBoardDescriptor: (core, META, boardNode, nodeHash) => {
            const board = [];
            for(let i=0;i<9;i+=1) {
                board.push(CONSTANTS.PIECE.EMPTY);
            }
            // Update the tile attributes to match the ones that tile have 
            core.getChildrenPaths(boardNode).forEach(tile => {
                const node = nodeHash[tile];
                const position_x = Number(core.getAttribute(node, 'row')) - 1;
                const position_y = Number(core.getAttribute(node, 'column')) - 1;
                // Calculate the position
                const position = position_x * 8 + position_y;
                let value = CONSTANTS.PIECE.EMPTY;
                const pieces = core.getChildrenPaths(node);
                if(pieces.length > 0) {
                    value = core.isInstanceOf(nodeHash[pieces[0]], META.Player) ? 
                        CONSTANTS.PIECE.X : CONSTANTS.PIECE.O;
                }
                board[position] = value;
            });
            return board;
        },
        getPositionHash: (core, boardNode, nodeHash) => {
            const hash = {};
            core.getChildrenPaths(boardNode).forEach(tile => {
                const node = nodeHash[tile];
                let value = CONSTANTS.PIECE.EMPTY;
                const position_x = Number(core.getAttribute(node, 'row')) - 1;
                const position_y = Number(core.getAttribute(node, 'column')) - 1;
                const position = position_x * 8 + position_y;
                hash[position] = core.getPath(node);
            });
            return hash;
        }
    }
});

