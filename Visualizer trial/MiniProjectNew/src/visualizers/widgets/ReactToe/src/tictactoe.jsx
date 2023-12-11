import React, {useCallback, useState} from 'react';
import Board from './board';
import CONSTANTS from './constants.js';

export default function TicTacToe({player, win, board}) {
    const getLabel = () => {
        let finished = true;
        board.forEach(piece => {
            if(piece === CONSTANTS.PIECE.EMPTY) {
                finished = false;

            }
        });
        if(finished) {
            return 'Game ended.';
        }
        
        if(player === CONSTANTS.PLAYER.O) {
            return 'Black Player moves...';
        } else {
            return 'White Player moves...';
        }
    }
   
    const str1 = String(win.black);
    const str2 = String(win.white);
    return (
    <div style={{ width: '100%', height: '100%', fontFamily:'fantasy', fontSize:'36px', fontWeight:'bold'}}>
        {getLabel()}
        <Board player={player} board={board} win={win}/>   
        <p>{str1 + str2}</p> 
    </div>
    
    );
}