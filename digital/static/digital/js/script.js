setTimeout(function(){
    document.getElementById('message').style.display = 'none';
}, 3000)


const orderBtn = document.querySelector('.my_orders')
    const listOrders = document.querySelector('.list_orders')
    const arrowDown = document.querySelector('.errow_down')
    orderBtn.addEventListener('click', () => {
      listOrders.classList.toggle('active')
      arrowDown.classList.toggle('active')
    })