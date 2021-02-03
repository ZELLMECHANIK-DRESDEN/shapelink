#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QDebug>
#include <QElapsedTimer>
#include <QFuture>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);


    QString listenPath = "tcp://*:5555";
    QtConcurrent::run(this, &MainWindow::run_zmqServer, listenPath);

}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::run_zmqServer(QString path)
{
    qDebug() << "ZMQ run server: " << path;

    zmq::socket_t sock = zmq::socket_t(zmqContext, zmq::socket_type::rep);
    sock.bind(path.toStdString().c_str());

    // PREALLOCATE
    zmq::message_t recvData;
    zmq::message_t sendData;
    sendData.rebuild(1);


    while(true)
    {
        sock.recv(recvData, zmq::recv_flags::none);
        //qDebug() << recvData.size();
        sock.send(sendData, zmq::send_flags::none);
    }
}

void MainWindow::run_zmqClient(QByteArray message, std::string path, quint64 n)
{
    zmq::message_t msg;
    QElapsedTimer timer;
    timer.start();

    double elapsed = 0.0;
    double time_sum = 0.0;
    double time_max = 0.0;
    double time_min = 99999.9;

    qint64 min_idx, max_idx;
    QVector<double> times;



    zmq::socket_t sock = zmq::socket_t(zmqContext, zmq::socket_type::req);
    sock.connect("tcp://localhost:5555");

    QThread::msleep(10);

    for (qint64 i=0; i<n; i++)
    {
        msg.rebuild(message.constData(), message.size());

        timer.restart();
        sock.send(msg, zmq::send_flags::none);
        sock.recv(msg, zmq::recv_flags::none);
        elapsed = timer.nsecsElapsed()/1000.0;
        time_sum += elapsed;
        if (time_max < elapsed) {
            time_max = elapsed;
            max_idx = i;
        }
        if (time_min > elapsed) {
            time_min = elapsed;
            min_idx = i;
        }

        times.append(elapsed);
    }
    qDebug() << "ZMQ" // << QString::fromStdString(msg.to_string())
             << "n:" << n
             << "size tx: " << message.size()
             << "avg:" << time_sum/(n)
             << "min:" << time_min << "(" << min_idx << ")"
             << "max:" << time_max << "(" << max_idx << ")"
             << "SD:"
             << "Bytes per sec: " << message.size()/time_sum*n*1000000;
}


void MainWindow::on_pushButton_clicked()
{

    QByteArray message = "MESSAGE";
    std::string path = "tcp://localhost:5555";


    for (int i = 1; i<7; i++)
    {
        // Try different message lenghts
        message.clear();
        message.resize(int(pow(10.0,i)));
        QFuture<void> fut = QtConcurrent::run(this, &MainWindow::run_zmqClient, message, path, 1000);
        fut.waitForFinished();
    }



}
