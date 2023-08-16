var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

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
                return React.createElement(
                    'tr',
                    { key: name },
                    React.createElement(
                        'td',
                        null,
                        name
                    ),
                    React.createElement(
                        'td',
                        null,
                        React.createElement(
                            'pre',
                            null,
                            content
                        )
                    ),
                    React.createElement(
                        'td',
                        null,
                        React.createElement(
                            'button',
                            null,
                            'Edit'
                        ),
                        React.createElement(
                            'button',
                            null,
                            'Delete'
                        )
                    )
                );
            })
        ),
        React.createElement(AddImage, null)
    );
}

function AddImage() {
    var _React$useState3 = React.useState(""),
        _React$useState4 = _slicedToArray(_React$useState3, 2),
        name = _React$useState4[0],
        setName = _React$useState4[1];

    return React.createElement(
        'div',
        null,
        React.createElement(
            'h2',
            null,
            'Add image'
        ),
        React.createElement(
            'form',
            null,
            React.createElement('input', { placeholder: 'Image name', type: 'text', value: name, onChange: function onChange(_ref2) {
                    var value = _ref2.target.value;
                    return setName(value.toUpperCase());
                } }),
            React.createElement(
                'button',
                null,
                'Add new image'
            )
        )
    );
}

ReactDOM.render(React.createElement(App, null), document.getElementById("root"));