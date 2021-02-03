#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QThread>
#include <QtConcurrent>
#include <QVector>
#include <QTimer>
#include <QByteArray>

#include <zmq.hpp>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void on_pushButton_clicked();

private:
    Ui::MainWindow *ui;

    zmq::context_t zmqContext;

    void run_zmqServer(QString path);

    void run_zmqClient(QByteArray message, std::string path, quint64 n);
};
#endif // MAINWINDOW_H
