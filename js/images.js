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

    onDelete = (name) => {
        fetch('/images/image/'+name, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(response => setImages(response.images))
    }

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
                        <button onClick={() => onDelete(name)}>Delete</button>
                    </td>
                </tr>
            )}
        </table>
        <AddImage onChange={setImages}/>
    </div>;
}

function AddImage({onChange}) {
    const [name, setName] = React.useState("");
    const onClick = () => {
        fetch('/images/image/' + name, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(response => onChange(response.images))
    };
    return <div>
        <h2>Add image</h2>
        <input placeholder="Image name" type="text" value={name} onChange={({ target: { value } }) => setName(value.toUpperCase())} />
        <button onClick={onClick}>Add new image</button>

    </div>;

}
  
ReactDOM.render(<App />, document.getElementById("root"));