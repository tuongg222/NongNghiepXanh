package vn.nongnghiep.xanh;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class CareReminderReceiver extends BroadcastReceiver {
    private static final String CHANNEL_ID = "nong_nghiep_xanh_care";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent != null && Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            CareReminderBridge.rescheduleAll(context);
            return;
        }

        String title = intent == null ? null : intent.getStringExtra("title");
        if (title == null || title.trim().isEmpty()) {
            title = "Lịch chăm sóc nông nghiệp";
        }

        NotificationManager manager =
                (NotificationManager) context.getSystemService(
                        Context.NOTIFICATION_SERVICE);

        if (manager == null) return;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Nhắc lịch chăm sóc",
                    NotificationManager.IMPORTANCE_DEFAULT);
            channel.setDescription("Nhắc công việc chăm sóc ruộng lúa");
            manager.createNotificationChannel(channel);
        }

        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(context, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(context);
        }

        builder.setSmallIcon(android.R.drawable.ic_dialog_info)
                .setContentTitle("Đến lịch chăm sóc!")
                .setContentText(title)
                .setAutoCancel(true)
                .setDefaults(Notification.DEFAULT_ALL);

        String id = intent == null ? null : intent.getStringExtra("reminder_id");
        int notificationId = id == null ? title.hashCode() : id.hashCode();

        manager.notify(notificationId, builder.build());
    }
}
