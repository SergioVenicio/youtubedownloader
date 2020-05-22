import React from 'react';
import axios from 'axios';

class Form extends React.Component {
  constructor (props) {
    super(props);
    this.state = {
      url: '',
      validUrl: false
    }

    this.urlChange = this.urlChange.bind(this);
    this.sendRequest = this.sendRequest.bind(this);
  }

  urlChange(event) {
    let validateURL = () => {
      return this.state.url && this.state.url.length > 0 && (
        this.state.url.startsWith('http://') || this.state.url.startsWith('https://'))
    }
    this.setState({ url: event.target.value })
    this.setState({ validUrl: validateURL() })
  }

  sendRequest(event){
    event.preventDefault();
    axios({
      method: 'post',
      url: 'http://localhost:8000/download',
      data: { url: this.state.url }
    }).then( response => {
      console.log(response);
      this.setState({ url: '' });
      this.setState({ validUrl: false });
    }).catch( error => {
      console.log(error);
    });
  }

  render() {
    return (
      <div className="form">
        <form>
          <input id='url' value={this.state.url} onChange={this.urlChange} />
          <br/>
          <button type='button' disabled={!this.state.validUrl} onClick={this.sendRequest}>Baixar</button>
        </form>
      </div>
    )
  }
}

export default Form