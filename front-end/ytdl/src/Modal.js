import React from 'react';

class Modal extends React.Component {
    constructor (props) {
        super(props)
    }

    render() {
        return (
            <div className="modal" style={{ display: this.props.show ? "block" : "none" }}>
                <div className="modal-background"></div>
                <div className="modal-card">
                    <div className="card">
                        <div className="card-content">
                            <div className="content">
                                { this.props.content }
                            </div>
                        </div>
                    </div>
                    <footer className="modal-card-foot">
                        <a href="#" className="button is-success" onClick={this.props.toggleModal}>Fechar</a>
                    </footer>
                </div>
            </div>
        )
    }
}

export default Modal;