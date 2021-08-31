import React from 'react';
import ReactDOM from 'react-dom'
//currentPageNumber, pageNumber, callBack, options
const PageNumber = (props) => {
    let className = "";
    if(props.currentPageNumber === props.pageNumber){
        className = "active"
    }
    return (
        <li className={className} onClick={()=>{
            ReactDOM.unmountComponentAtNode(props.divElement)
            props.callBack(props.pageNumber, props.options)
        }}><a style={{cursor:"pointer"}}>{props.pageNumber}</a></li>
    );
}

export default PageNumber