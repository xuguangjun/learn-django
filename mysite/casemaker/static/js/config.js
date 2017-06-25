var ischeck = false;
function checkForm(){
        if(!ischeck){
            ischeck=true;
        }else{
            alert("正在生成case，无需重复提交！");
            ischeck=false;
        }
        return ischeck;
    }