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

    const url = '/images/image/'+name;

    React.useEffect(() => setEditableContent(content), [content]);

    onDelete = () => {
        fetch(url, {
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
        fetch(url, {
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
            {editState === "view" && <button onClick={() => setEditState('edit_text')}>Edit (Text)</button>}
            {(editState === "edit" || editState === "edit_text") && <button onClick={onSave}>Save</button>}
            {editState === "saving" && <div>Saving...</div>}
            <br />
            <button onClick={() => onDelete()}>Delete</button>
        </td>
        <td>
            <ImageEditor content={editableContent} onChange={setEditableContent} editable={editState === "edit"} useText={editState === "edit_text"} />
        </td>
    </tr>;
}

function ImageEditor({editable, content, onChange, useText}) {
    const toArray = (inputString) => inputString.split("\n").map(r => r.split('').map(c => c === "█"));
    const toString = (inputArray) => inputArray.map(r => r.map(c => c ? "█" : "░").join("")).join("\n");

    const contentAsArray = React.useMemo(() => toArray(content), [content]);
    const onChangeInternal = (x, y) => {
        if (!editable) {
            return;
        }
        const newContent = [...contentAsArray];
        newContent[y][x] = !newContent[y][x];
        onChange(toString(newContent));
    }

    if (useText) {
        return <textarea rows={7} cols={84} onChange={e => onChange(e.target.value)}>{toString(contentAsArray)}</textarea>
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