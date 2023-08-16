var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

function App() {
    var _React$useState = React.useState(null),
        _React$useState2 = _slicedToArray(_React$useState, 2),
        images = _React$useState2[0],
        setImages = _React$useState2[1];

    React.useEffect(function () {
        fetch('/images/list', {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        }).then(function (response) {
            return response.json();
        }).then(function (response) {
            return setImages(response.images);
        });
    }, []);

    if (images === null) {
        return React.createElement(
            'div',
            null,
            'Loading...'
        );
    }

    return React.createElement(
        'div',
        null,
        React.createElement(
            'h1',
            null,
            'Images'
        ),
        React.createElement(
            'table',
            null,
            images.map(function (_ref) {
                var name = _ref.name,
                    content = _ref.content;
                return React.createElement(Image, { content: content, name: name, key: name, setImages: setImages });
            })
        ),
        React.createElement(AddImage, { onChange: setImages })
    );
}

function AddImage(_ref2) {
    var onChange = _ref2.onChange;

    var _React$useState3 = React.useState(""),
        _React$useState4 = _slicedToArray(_React$useState3, 2),
        name = _React$useState4[0],
        setName = _React$useState4[1];

    var onClick = function onClick() {
        fetch('/images/image/' + name, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json'
            }
        }).then(function (response) {
            return response.json();
        }).then(function (response) {
            return onChange(response.images);
        });
    };
    return React.createElement(
        'div',
        null,
        React.createElement(
            'h2',
            null,
            'Add image'
        ),
        React.createElement('input', { placeholder: 'Image name', type: 'text', value: name, onChange: function onChange(_ref3) {
                var value = _ref3.target.value;
                return setName(value.toUpperCase());
            } }),
        React.createElement(
            'button',
            { onClick: onClick },
            'Add new image'
        )
    );
}

function Image(_ref4) {
    var name = _ref4.name,
        content = _ref4.content,
        setImages = _ref4.setImages;

    var _React$useState5 = React.useState("view"),
        _React$useState6 = _slicedToArray(_React$useState5, 2),
        editState = _React$useState6[0],
        setEditState = _React$useState6[1];

    var _React$useState7 = React.useState(""),
        _React$useState8 = _slicedToArray(_React$useState7, 2),
        editableContent = _React$useState8[0],
        setEditableContent = _React$useState8[1];

    React.useEffect(function () {
        return setEditableContent(content);
    }, [content]);

    onDelete = function onDelete() {
        fetch('/images/image/' + name, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json'
            }
        }).then(function (response) {
            return response.json();
        }).then(function (response) {
            return setImages(response.images);
        });
    };

    onSave = function onSave() {
        setEditState('saving');
        var body = new FormData();
        body.append('content', editableContent);
        fetch('/images/image/' + name, {
            method: 'PUT',
            body: body,
            headers: {
                'Accept': 'application/json'
            }
        }).then(function (response) {
            return response.json();
        }).then(function (response) {
            setEditState('view');
            setImages(response.images);
        });
    };
    return React.createElement(
        'tr',
        null,
        React.createElement(
            'td',
            null,
            name,
            React.createElement('br', null),
            editState === "view" && React.createElement(
                'button',
                { onClick: function onClick() {
                        return setEditState('edit');
                    } },
                'Edit'
            ),
            editState === "edit" && React.createElement(
                'button',
                { onClick: onSave },
                'Save'
            ),
            editState === "saving" && React.createElement(
                'div',
                null,
                'Saving...'
            ),
            React.createElement('br', null),
            React.createElement(
                'button',
                { onClick: function onClick() {
                        return onDelete();
                    } },
                'Delete'
            )
        ),
        React.createElement(
            'td',
            null,
            React.createElement(ImageEditor, { content: editableContent, onChange: setEditableContent, editable: editState === "edit" })
        )
    );
}

function ImageEditor(_ref5) {
    var editable = _ref5.editable,
        content = _ref5.content,
        onChange = _ref5.onChange;

    var contentAsArray = React.useMemo(function () {
        return content.split("\n").map(function (r) {
            return r.split('').map(function (c) {
                return c === "█";
            });
        });
    }, [content]);
    console.log(contentAsArray);

    var onChangeInternal = function onChangeInternal(x, y) {
        if (!editable) {
            return;
        }
        var newContent = [].concat(_toConsumableArray(contentAsArray));
        newContent[y][x] = !newContent[y][x];
        onChange(newContent.map(function (r) {
            return r.map(function (c) {
                return c ? "█" : "░";
            }).join("");
        }).join("\n"));
    };

    return React.createElement(
        'table',
        { className: "flipdot " + (editable ? "flipdot--editable" : "") },
        contentAsArray.map(function (row, y) {
            return React.createElement(
                'tr',
                { key: y },
                row.map(function (cell, x) {
                    return React.createElement('td', {
                        key: x,
                        className: "flipdot-cell " + (cell ? 'flipdot-cell--true' : 'flipdot-cell--false'),
                        onClick: function onClick() {
                            return onChangeInternal(x, y);
                        }
                    });
                })
            );
        })
    );
}

ReactDOM.render(React.createElement(App, null), document.getElementById("root"));