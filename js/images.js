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
                <Image content={content} name={name} key={name} setImages={setImages} />
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

function Image({name, content, setImages}) {
    const [editState, setEditState] = React.useState("view");
    const [editableContent, setEditableContent] = React.useState("");

    React.useEffect(() => setEditableContent(content), [content]);

    onDelete = () => {
        fetch('/images/image/'+name, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(response => setImages(response.images))
    }

    onSave = () => {
        setEditState('saving');
        let body = new FormData();
        body.append('content', editableContent);
        fetch('/images/image/'+name, {
            method: 'PUT',
            body,
            headers: {
                'Accept': 'application/json',
            },
        })
        .then(response => response.json())
        .then(response => {
            setEditState('view');
            setImages(response.images);
        })
    }
    return <tr>
        <td>
            {name}<br />
            {editState === "view" && <button onClick={() => setEditState('edit')}>Edit</button>}
            {editState === "edit" && <button onClick={onSave}>Save</button>}
            {editState === "saving" && <div>Saving...</div>}
            <br />
            <button onClick={() => onDelete()}>Delete</button>
        </td>
        <td>
            <ImageEditor content={editableContent} onChange={setEditableContent} editable={editState === "edit"} />
        </td>
    </tr>;
}

function ImageEditor({editable, content, onChange}) {
    const contentAsArray = React.useMemo(() => {
        return content.split("\n").map(r => r.split('').map(c => c === "█"));   
    }, [content]);
    console.log(contentAsArray);

    const onChangeInternal = (x, y) => {
        if (!editable) {
            return;
        }
        let newContent = [...contentAsArray];
        newContent[y][x] = !newContent[y][x];
        onChange(newContent.map(r => r.map(c => c ? "█" : "░").join("")).join("\n"));
    }

    return <table className={"flipdot "+(editable ? "flipdot--editable": "")}>
        {contentAsArray.map((row, y) => 
            <tr key={y}>
                {row.map((cell, x) => 
                    <td 
                        key={x} 
                        className={"flipdot-cell " + (cell ? 'flipdot-cell--true' : 'flipdot-cell--false')}
                        onClick={() => onChangeInternal(x, y)}
                    />
                )}
            </tr>
        )}

    </table>;
}
  
ReactDOM.render(<App />, document.getElementById("root"));