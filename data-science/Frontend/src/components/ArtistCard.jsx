import React from "react"

function ArtistCard({artist}) {
    return (
        <li style={{ margin: "10 px 0", listStyle: "none", display: "flex", alignItems: "center"}}>
            <img 
                src={artist.img_url}
                alt={artist.name}
                style={{ width: "50px", height: "50px", marginRight: "10px", borderRadius: "50%"}}
                />
            {artist.name} - {artist.genre}
        </li>
    )
}

export default ArtistCard; 