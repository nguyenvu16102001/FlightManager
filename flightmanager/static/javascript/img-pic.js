var i=1;
changeimg=function(){
    var img=["https://res.cloudinary.com/du3xpvajy/image/upload/v1641519831/cnpm/Halong_ensemble__colour_corrected_ewsvep.jpg",
            "https://res.cloudinary.com/du3xpvajy/image/upload/v1641520899/cnpm/hoi-an-quang-nam-vntrip-1_bb6jir.jpg",
            "https://res.cloudinary.com/du3xpvajy/image/upload/v1641520961/cnpm/qb_1-1603825054413_x1wikr.jpg",
            "https://res.cloudinary.com/du3xpvajy/image/upload/v1641521044/cnpm/gioi-thieu-ve-ho-guom-15_kid67a.jpg",
            "https://res.cloudinary.com/du3xpvajy/image/upload/v1641521077/cnpm/111111_xvqfrc.jpg",
            "https://res.cloudinary.com/du3xpvajy/image/upload/v1641521127/cnpm/thanh_pho_bien_vung_tau_293dcb18853648c39e99a09dc7b52f27_na5imk.jpg"]
    var name=["Vịnh Hạ Long","Phố cổ Hội An", "Khu du lịch Quảng Bình","Hồ Gươm","Khu du lịch Đà Nẵng","Khu du lịch Vũng tàu"]
            document.getElementById("img-news").src=img[i];
            document.getElementById("name-pic").innerHTML=name[i];
    i++;
    if(i==6)
    {
        i=0;
    }
}
changename = function(){
    var name=["Vịnh Hạ Long","Hội An", "Khu du lịch Quảng Bình","Hồ Gươm","Khu du lịch Đà Nẵng","Khu du lịch Vũng tàu"]

}
setInterval(changeimg,5000);