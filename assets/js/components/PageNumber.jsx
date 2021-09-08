import React from 'react';
import ReactDOM from 'react-dom'
//currentPageNumber, pageNumber, callBack, options
const PageNumber = (props) => {
    let className = "";
    if (props.currentPageNumber === props.pageNumber) {
        className = "active"
    }
    let onClickHandler = () => {
        ReactDOM.unmountComponentAtNode(props.divElement)
        props.callBack(props.pageNumber, props.options)
    }
    return (
        <li className={className} onClick={isNaN(props.pageNumber) ? undefined : onClickHandler}><a
            style={{cursor: isNaN(props.pageNumber) ? "auto" : "pointer"}}>{props.pageNumber}</a></li>
    );
}

export default PageNumber