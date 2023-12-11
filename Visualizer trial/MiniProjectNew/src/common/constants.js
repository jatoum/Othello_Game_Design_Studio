//In here we assume tht Player.0 is black player (starts first) and player x is white player
define(['./constants'], function (CONSTANTS) {
    return {
        PLAYER: {
            O:'o',
            X:'x'
        },
        PIECE: {
            O: 'o',
            X: 'x',
            EMPTY: '-'
        }
    }
});