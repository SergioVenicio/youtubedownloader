import React from 'react';
import axios from 'axios';
import Modal from './Modal';

class Form extends React.Component {
  constructor (props) {
    super(props);
    this.state = {
      url: '',
      validUrl: false,
      showModal: false,
    }

    this.urlChange = this.urlChange.bind(this);
    this.sendRequest = this.sendRequest.bind(this);
    this.toggleModal = this.toggleModal.bind(this);
  }

  toggleModal(e) {
    console.log(e)
    this.setState({
      showModal: !this.state.showModal,
    });
  }

  urlChange(event) {
    let url = String(event.target.value);
    let urlRegex = new RegExp("^https:\/\/(www\.)?[a-zA-Z].{1,}")

    this.setState({ 
      url, validUrl: urlRegex.test(url)
    })
  }

  sendRequest(event){
    event.preventDefault();
    axios({
      method: 'post',
      url: 'http://localhost:8000/download',
      data: { url: this.state.url }
    }).then( () => {
      this.setState({ 
        url: '',
        validUrl: false,
        showModal: true
      });
    }).catch( error => {
      console.log(error);
    });
  }

  render() {
    return (
      <section className="section">
        <div className="container">
          <form>
            <div className="field field has-addons has-addons-center">
              <div className="control">
                <input className="input" id='url' value={this.state.url} onChange={this.urlChange} placeholder="Insira o link valido!" />  
                { !this.state.validUrl ? <p style={{textAlign:"center"}} className="help is-danger" id='urlHelp'>URL inválida</p> : null }
              </div>
              <p className="control">
                <button className="button is-black" type='button' disabled={!this.state.validUrl} onClick={this.sendRequest}>Baixar</button>
              </p>
            </div>
          </form>
        </div>
        <Modal
          show={this.state.showModal}
          content="Download iniciado com sucesso!"
          toggleModal={this.toggleModal}/>
      </section>
    )
  }
}

export default Form