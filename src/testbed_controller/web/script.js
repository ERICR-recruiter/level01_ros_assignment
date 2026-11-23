// ROS connection
let ros = null;

// Publishers
let cmdVelPublisher = null;
let emergencyPublisher = null;

// Connection state
let connected = false;

// Joystick elements
const joystickBase = document.getElementById("joystick-base");
const joystickStick = document.getElementById("joystick-stick");

const connectButton = document.getElementById("connect-btn");
const emergencyButton = document.getElementById("emergency-btn");

const statusText = document.getElementById("connection-status");
const indicator = document.getElementById("connection-indicator");

// Velocity limits
const MAX_LINEAR = 0.5;
const MAX_ANGULAR = 1.0;

// Joystick state
let active = false;
let linearVelocity = 0;
let angularVelocity = 0;

const radius = 70;


// Connect to ROS
connectButton.addEventListener("click", function () {

    if (connected) {
        ros.close();
        return;
    }

    ros = new ROSLIB.Ros({
        url: "ws://" + window.location.hostname + ":9090"
    });

    ros.on("connection", function () {

        connected = true;

        statusText.textContent = "Connected";
        indicator.style.background = "lime";

        connectButton.textContent = "Disconnect";

        cmdVelPublisher = new ROSLIB.Topic({
            ros: ros,
            name: "/web/cmd_vel",
            messageType: "geometry_msgs/msg/Twist"
        });

        emergencyPublisher = new ROSLIB.Topic({
            ros: ros,
            name: "/web/emergency_stop",
            messageType: "std_msgs/msg/Bool"
        });

        console.log("Connected to ROS 2 Humble");

    });

    ros.on("error", function (error) {

        console.error(error);

    });

    ros.on("close", function () {

        connected = false;

        statusText.textContent = "Disconnected";
        indicator.style.background = "red";

        connectButton.textContent = "Connect";

        resetJoystick();

    });

});


// Publish velocity
function publishVelocity() {

    if (!connected || !cmdVelPublisher) {
        return;
    }

    const message = new ROSLIB.Message({

        linear: {
            x: linearVelocity,
            y: 0.0,
            z: 0.0
        },

        angular: {
            x: 0.0,
            y: 0.0,
            z: angularVelocity
        }

    });

    cmdVelPublisher.publish(message);

}


// Joystick movement
function moveJoystick(event) {

    if (!active) return;

    const rect = joystickBase.getBoundingClientRect();

    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    let dx = event.clientX - centerX;
    let dy = event.clientY - centerY;

    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > radius) {

        dx = dx * radius / distance;
        dy = dy * radius / distance;

    }

    joystickStick.style.left =
        `calc(50% + ${dx}px)`;

    joystickStick.style.top =
        `calc(50% + ${dy}px)`;

    // Forward / reverse
    linearVelocity = (-dy / radius) * MAX_LINEAR;

    // Left / right
    angularVelocity = (-dx / radius) * MAX_ANGULAR;

    document.getElementById("linear-value").textContent =
        linearVelocity.toFixed(2) + " m/s";

    document.getElementById("angular-value").textContent =
        angularVelocity.toFixed(2) + " rad/s";

}


// Reset joystick
function resetJoystick() {

    active = false;

    joystickStick.style.left = "50%";
    joystickStick.style.top = "50%";

    linearVelocity = 0;
    angularVelocity = 0;

    document.getElementById("linear-value").textContent =
        "0.00 m/s";

    document.getElementById("angular-value").textContent =
        "0.00 rad/s";

    publishVelocity();

}


// Mouse and touch support
joystickBase.addEventListener("pointerdown", function (event) {

    if (!connected) return;

    active = true;

    joystickBase.setPointerCapture(event.pointerId);

    moveJoystick(event);

});

joystickBase.addEventListener("pointermove", moveJoystick);

joystickBase.addEventListener("pointerup", resetJoystick);

joystickBase.addEventListener("pointercancel", resetJoystick);


// Publish commands at 10 Hz while connected.
// Publish zero when joystick is released.
setInterval(function () {

    if (connected) {

        publishVelocity();

    }

}, 100);


// Emergency stop
emergencyButton.addEventListener("click", function () {

    if (!connected || !emergencyPublisher) return;

    resetJoystick();

    emergencyPublisher.publish(
        new ROSLIB.Message({
            data: true
        })
    );

});