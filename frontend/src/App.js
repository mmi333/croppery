import './App.css';

function App() {
  const handleSubmit = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target);
    
    const Upload = async() => {
      await fetch('/api/upload', {
        method: 'POST',
        body: formData
      }).then(resp => {
        resp.json().then(data => {console.log(data)})
      })
    }
    Upload();
  }

  return (
    <div className="App">
      <form onSubmit={handleSubmit} className="container mt-5 pt-5 pb-5" enctype="multipart/form-data">
    <div className="form-inline justify-content-center mt-5">
        <label htmlFor="image" className="ml-sm-4 font-weight-bold mr-md-4">Image :  </label>
        <div className="input-group">
            <input type="file" id="image" name="file" 
            accept="image/*" className="file-custom"/>
        </div>
    </div>

    <div className="input-group justify-content-center mt-4">
        <button type="submit" className="btn btn-md btn-primary">Upload,,,</button>
    </div>
</form>

    </div>
  );
}

export default App;
