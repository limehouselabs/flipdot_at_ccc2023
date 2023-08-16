function App() {
    const [images, setImages] = React.useState(null);

    React.useEffect(() => {
        fetch('/images/list', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(response => setImages(response.images))
    }, []);

    if (images === null) {
        return <div>Loading...</div>;
    }



    return <div>
        <h1>Images</h1>
        <table>
            {images.map(({name, content}) => 
                <tr key={name}>
                    <td>{name}</td>
                    <td><pre>{content}</pre></td>
                    <td>
                        <button>Edit</button>
                        <button>Delete</button>
                    </td>
                </tr>
            )}
        </table>
        <AddImage />
    </div>;
}

function AddImage() {
    const [name, setName] = React.useState("");
    return <div>
        <h2>Add image</h2>
        <form>
            <input placeholder="Image name" type="text" value={name} onChange={({ target: { value } }) => setName(value.toUpperCase())} />
            <button>Add new image</button>
        </form>
    </div>;

}
  
ReactDOM.render(<App />, document.getElementById("root"));