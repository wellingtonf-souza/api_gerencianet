function copyCode(){
    const textarea = document.createElement('textarea');
    textarea.value = document.getElementById('copy').value
    document.body.appendChild(textarea)
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

function modal(){
    Swal.fire({
        title: 'Estamos processando a requisição',
        willOpen:()=>{
            Swal.showLoading()
        }
    })
}