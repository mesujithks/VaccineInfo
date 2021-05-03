// this is the code which will be injected into a given page...
(function () {
  function isMyScriptLoaded(url) {
    if (!url) url = "http://xxx.co.uk/xxx/script.js";
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length; i--; ) {
      if (scripts[i].src == url) return true;
    }
    return false;
  }

  if (
    !isMyScriptLoaded(
      "https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"
    )
  ) {
    var script = document.createElement("script");
    script.src =
      "https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js";
    /* If you need callback */
    script.onload = script.onreadystatechange = function () {};
    /* end */
    document.body.appendChild(script);

    var curentCity = "";

    function isExist(list, key) {
      return list.includes(key);
    }

    function sendNotification(count) {
      let dataObject = {};
      let dataList = [];
      for (let i = 0; i < count; i++) {
        for (let j = 0; j < 7; j++) {
          let index = j + i * 7;
          let val = $($(".vaccine-box > a")[index]).text().trim().toLowerCase();

          if (val != "booked" && val != "na") {
            var data = {};
            data.location = $($(".center-name-title")[i]).text();
            let temp = $($(".center-name-text")[i]).text().split(",");
            data.city = temp[0].trim();
            data.state = temp[1].trim();
            data.pincode = temp[2].trim();
            data.count = val;
            let arr = dataList.filter((item) => item.location == data.location);
            if (arr.length == 0) {
              dataList.push(data);
            } else if (arr.length == 1) {
              dataList[dataList.indexOf(arr[0])].count = (
                Number(count) + Number(dataList[dataList.indexOf(arr[0])].count)
              ).toString();
            }
          }
        }
      }
      if (dataList.length > 0) {
        dataObject.city = dataList[0].city;
        dataObject.data = dataList;
        $.ajax({
          type: "POST",
          contentType: "application/json",
          dataType: "application/json",
          data: JSON.stringify(dataObject),
          crossDomain: true,
          url: "http://127.0.0.1:5000//API/publish",
          success: function (res) {
            console.log(res);
          },
        });
      }
    }

    function sendTokenExpNotification() {
      let dataObject = {};
      dataObject.city = curentCity;
      $.ajax({
        type: "POST",
        contentType: "application/json",
        dataType: "application/json",
        data: JSON.stringify(dataObject),
        crossDomain: true,
        url: "http://127.0.0.1:5000//API/notifyAdmin",
        success: function (res) {
          console.log(res);
        },
      });
    }

    var oldLength = 0;
    var errorMsgSent = false;
    var globalList = [];

    var repeat = window.setInterval(function () {
      $(".pin-search-btn").click();
      setTimeout(function () {
        var count = $(".mat-selection-list > div").length;
        console.log(count);
        let tempList = [];
        for (let i = 0; i < count; i++) {
          if (i == 0)
            curentCity = $($(".center-name-text")[i])
              .text()
              .split(",")[0]
              .trim();
          for (let j = 0; j < 7; j++) {
            let index = j + i * 7;
            let val = $($(".vaccine-box > a")[index])
              .text()
              .trim()
              .toLowerCase();
            if (val != "booked" && val != "na") {
              let location = $($(".center-name-title")[i]).text();
              if (!isExist(tempList, location)) tempList.push(location);
            }
          }
        }

        if (
          count > 0 &&
          JSON.stringify(globalList.sort()) != JSON.stringify(tempList.sort())
        ) {
          globalList = tempList;
          sendNotification(count);
          /* var r = confirm("Need to exit?");
          if (r == true) {
            window.clearInterval(repeat);
          } */
        }
        oldLength = count;
      }, 1000);
      if (
        window.location.href !=
          "https://selfregistration.cowin.gov.in/appointment" &&
        !errorMsgSent
      ) {
        sendTokenExpNotification();
        errorMsgSent = true;
      } else if (
        window.location.href ==
        "https://selfregistration.cowin.gov.in/appointment"
      ) {
        errorMsgSent = false;
      }
    }, 5000);
  }
})();
