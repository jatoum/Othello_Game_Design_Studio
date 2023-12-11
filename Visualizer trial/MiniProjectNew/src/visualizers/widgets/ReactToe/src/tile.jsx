import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { icon } from '@fortawesome/fontawesome-svg-core/import.macro'
import { useState } from 'react';
import CONSTANTS from './constants.js';

export default function Tile({player, piece, position, win}) {

    const [hasMouse, setMouse, onHasMouseChange] = useState(false);

    const onTileClick = () => {
        if (piece === CONSTANTS.PIECE.EMPTY) {
            WEBGME_CONTROL.flipping();
        }
    }

    const onMouseEnter = () => {
        setMouse(true);
    }

    const onMouseLeave = () => {
        setMouse(false);
    }
    
    const getPiece = () => {
        console.log('GP:',player,piece,position,win);
        const styleB = {fontSize:'90px', paddingLeft:'8px',paddingTop:'2px'};
        const styleW = {fontSize:'90px', paddingLeft:'13px',paddingTop:'2px'};
        const dStyle = player === CONSTANTS.PLAYER.O ? 
            JSON.parse(JSON.stringify(styleB)) : 
            JSON.parse(JSON.stringify(styleW));
        dStyle.opacity = 0.5;

        let style = dStyle;
        let myIcon = null;
        switch (piece) {
            case CONSTANTS.PIECE.O:
                style = styleB;
                myIcon = icon({name:'o', family:'classic', style:'solid'});
                // Black circle #000000
                myIcon.backgroundColor= '#000000';
                myIcon.border= '#000000';
                break;
            case CONSTANTS.PIECE.X:
                style = styleW;
                myIcon = icon({name:'o', family:'classic', style:'solid'});
                // White circle #ffffff 
                myIcon.backgroundColor = '#ffffff';
                myIcon.borderColor = '#000000';
                break;
            default:
                if(hasMouse) {
                    if(player === CONSTANTS.PLAYER.O) {
                        myIcon = icon({name:'o', family:'classic', style:'solid'});
                        myIcon.backgroundColor= '#000000';
                        myIcon.border= '#000000';
                    } else {
                        myIcon = icon({name:'o', family:'classic', style:'solid'});
                        myIcon.backgroundColor = '#ffffff';
                        myIcon.borderColor = '#000000';
                    }
                }
        }

        if(myIcon !== null) {
            return (<FontAwesomeIcon style={style} icon={myIcon} size='xl'/>); 
        }

        return null;
    }

    const getTile = () => {
        const style = {
            width:'100px', 
            height:'100px', 
            borderColor:'black',
            borderWidth:'2px',
            border:'solid'};

            return (<div onClick={onTileClick} 
                style={style}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}>{getPiece()}</div>);
    }

    return getTile();
}