import React from 'react';
import PageNumber from './PageNumber';

//(firstElement, lastElement, totalElements, currentPageNumber, totalPages, paginationContainer, callBack, options)
const Pagination = (props) => {
    let pageNumberElements = []
    if(props.totalPages < 7) {
        for (let i = 1; i <= props.totalPages; i++) {
            pageNumberElements.push(<PageNumber {...props} pageNumber={i} key={i}/>)
        }
    } else {
        if(props.currentPageNumber < 4) {
            pageNumberElements.push(<PageNumber {...props} pageNumber={1} key={1}/>)
            if (props.currentPageNumber < 4) {
                for (let i = 2; i < 5; i++) {
                    pageNumberElements.push(<PageNumber {...props} pageNumber={i} key={i}/>)
                }
                pageNumberElements.push(<PageNumber {...props} pageNumber={".."} key={".."}/>)
                pageNumberElements.push(<PageNumber {...props} pageNumber={props.totalPages} key={props.totalPages}/>)
            }
        }
        if(props.currentPageNumber >= 4){
            pageNumberElements.push(<PageNumber {...props} pageNumber={1} key={1}/>)
            pageNumberElements.push(<PageNumber {...props} pageNumber={".."} key={"..v1"}/>)
            if(props.currentPageNumber < props.totalPages - 3){
                for(let i = props.currentPageNumber - 1; i < props.currentPageNumber +2; i++){
                    pageNumberElements.push(<PageNumber {...props} pageNumber={i} key={i}/>)
                }
                pageNumberElements.push(<PageNumber {...props} pageNumber={".."} key={"..v2"}/>)
                pageNumberElements.push(<PageNumber {...props} pageNumber={props.totalPages} key={props.totalPages}/>)
            } else {
                for(let i = props.currentPageNumber - 1; i <= props.totalPages; i++){
                    pageNumberElements.push(<PageNumber {...props} pageNumber={i} key={i}/>)
                }
            }
        }
    }

    return(
    <div className="row no-gutters">
        <div className="col-12 col-md">
            <div className="pagination-data">Showing {props.firstElement} to {props.lastElement} of {props.totalElements} entries</div>
        </div>
        <div className="col-12 col-md-auto">
            <ul className="pagination">
                {pageNumberElements}
            </ul>
        </div>
    </div>
    );
}

export default Pagination