// CODE
const endDate = new Date(
    endYear,
    endMonth - 1,
    endDay,
    endHour,
    endMinutes,
    endSeconds,
);

Date.prototype.getAbsDays = function () {
    return Math.floor(this / 1000 / 86400)
};

function for2sumb(number) {
    return number < 10 ? '0' + number : number
}

function declensionByCases(number, type='minutes') {
    number = number > 20 ? number % 10 : number;
    switch (number) {
        case 1:
            return {
                days: "день",
                hours: "час",
                minutes: "минута",
                seconds: "секунда"
            }[type];
        case 2:
        case 3:
        case 4:
            return {
                days: "дня",
                hours: "часa",
                minutes: "минуты",
                seconds: "секунды"
            }[type];
        default:
            return {
                days: "дней",
                hours: "часов",
                minutes: "минут",
                seconds: "секунд"
            }[type]
    }
}

function updateTimer() {
    let nowDate        = new Date(),
        differenceDate = new Date(Math.abs(nowDate - endDate));

    let days    = differenceDate.getAbsDays(),
        hours   = differenceDate.getUTCHours(),
        minutes = differenceDate.getUTCMinutes(),
        seconds = differenceDate.getUTCSeconds();

    document.getElementById('number-days').innerText    = for2sumb(days);
    document.getElementById('number-hours').innerText   = for2sumb(hours);
    document.getElementById('number-minutes').innerText = for2sumb(minutes);
    document.getElementById('number-seconds').innerText = for2sumb(seconds);

    document.getElementById('string-days').innerText    = declensionByCases(days, "days");
    document.getElementById('string-hours').innerText   = declensionByCases(hours, "hours");
    document.getElementById('string-minutes').innerText = declensionByCases(minutes, "minutes");
    document.getElementById('string-seconds').innerText = declensionByCases(seconds, "seconds");
}

function startTimer() {
    let header = document.getElementById("timer-header");
    let nowDate = new Date();
    if (nowDate > endDate) {
        document.getElementById("timer-block").innerHTML = "";
        header.innerText = endMessage
    } else {
        header.innerText = startMessage;

        updateTimer();
        setInterval(updateTimer, 1000)
    }
}