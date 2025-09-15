import React, {useState} from "react"

 // Creating the SearchBar component
function SearchBar(){
    const [searchText, setSearchText] = useState("");   //Function to dynamically update query text 
    const [results, setResults] = useState([]);     //Dynamically update results 
    
    const handleSubmit = async(event) => {
        event.preventDefault(); 
        const response = await fetch('/api/search?query=${searchText}'); 
        const data = await response.json(); 
        setResults(data); 
    };    
}

//Returning HTML components that correspond to functionality just described above
return (
    <div style = {{ margin : 20}}>
        <form onSubmit={handleSubmit}>
            <input type="text" value = {searchText} onChange={e => setSearchText(e.target.value)} placeholder="Search..."/>
            <button type="submit">Search</button>
        </form>

        <ul>
            {results.map((artist, i) => (
                <ArtistCard key={i} artist = {artist}/>
            ))}
        </ul>
    </div>
)