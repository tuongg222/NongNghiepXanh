package vn.nongnghiep.xanh;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.webkit.JavascriptInterface;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class CareReminderBridge {
    private final Context context;

    public CareReminderBridge(Context context) {
        this.context = context.getApplicationContext();
    }

    @JavascriptInterface
    public void scheduleReminder(String id, String title, String date, String time) {
        if (id == null || id.trim().isEmpty()
                || title == null || title.trim().isEmpty()
                || date == null || date.trim().isEmpty()) {
            return;
        }

        try {
            String safeTime = (time == null || time.trim().isEmpty()) ? "09:00" : time.trim();
            SimpleDateFormat format =
                    new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US);
            format.setLenient(false);
            Date parsed = format.parse(date + " " + safeTime);
            if (parsed == null) return;

            Calendar calendar = Calendar.getInstance();
            calendar.setTime(parsed);
            calendar.set(Calendar.SECOND, 0);
            calendar.set(Calendar.MILLISECOND, 0);

            long triggerAt = calendar.getTimeInMillis();
            long now = System.currentTimeMillis();

            if (triggerAt < now) {
                Calendar today = Calendar.getInstance();
                boolean isToday =
                        today.get(Calendar.YEAR) == calendar.get(Calendar.YEAR)
                        && today.get(Calendar.DAY_OF_YEAR)
                        == calendar.get(Calendar.DAY_OF_YEAR);

                if (!isToday) return;
                triggerAt = now + 60_000L;
            }

            Intent intent = new Intent(context, CareReminderReceiver.class);
            intent.setAction("vn.nongnghiep.xanh.CARE_REMINDER");
            intent.putExtra("title", title);
            intent.putExtra("reminder_id", id);

            PendingIntent pendingIntent = PendingIntent.getBroadcast(
                    context,
                    id.hashCode(),
                    intent,
                    PendingIntent.FLAG_UPDATE_CURRENT
                            | PendingIntent.FLAG_IMMUTABLE
            );

            AlarmManager alarmManager =
                    (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
            if (alarmManager != null) {
                alarmManager.setAndAllowWhileIdle(
                        AlarmManager.RTC_WAKEUP,
                        triggerAt,
                        pendingIntent
                );
            }
        } catch (Exception ignored) {
            // Bỏ qua ngày không hợp lệ để ứng dụng không bị dừng.
        }
    }

    @JavascriptInterface
    public void cancelReminder(String id) {
        if (id == null || id.trim().isEmpty()) return;

        Intent intent = new Intent(context, CareReminderReceiver.class);
        intent.setAction("vn.nongnghiep.xanh.CARE_REMINDER");

        PendingIntent pendingIntent = PendingIntent.getBroadcast(
                context,
                id.hashCode(),
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT
                        | PendingIntent.FLAG_IMMUTABLE
        );

        AlarmManager alarmManager =
                (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (alarmManager != null) {
            alarmManager.cancel(pendingIntent);
        }
        pendingIntent.cancel();
    }
}
