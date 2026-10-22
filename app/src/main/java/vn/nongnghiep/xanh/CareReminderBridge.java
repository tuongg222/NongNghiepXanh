package vn.nongnghiep.xanh;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.webkit.JavascriptInterface;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.Map;

public class CareReminderBridge {
    static final String PREFS = "nx_care_reminders";
    private static final String ACTION = "vn.nongnghiep.xanh.CARE_REMINDER";
    private final Context context;

    public CareReminderBridge(Context context) {
        this.context = context.getApplicationContext();
    }

    @JavascriptInterface
    public void scheduleReminder(String id, String title, String date, String time) {
        if (id == null || id.trim().isEmpty()
                || title == null || title.trim().isEmpty()
                || date == null || date.trim().isEmpty()) return;

        String safeTime = (time == null || time.trim().isEmpty()) ? "09:00" : time.trim();
        try {
            SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US);
            format.setLenient(false);
            Date parsed = format.parse(date + " " + safeTime);
            if (parsed == null) return;

            long triggerAt = parsed.getTime();
            if (triggerAt <= System.currentTimeMillis()) {
                // Không đặt báo thức cho lịch đã qua.
                cancelAlarm(id);
                context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().remove(id).apply();
                return;
            }

            String packed = title + "\n" + date + "\n" + safeTime;
            context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                    .edit().putString(id, packed).apply();
            scheduleAt(id, title, triggerAt);
        } catch (Exception ignored) {
            // Không làm ứng dụng dừng nếu ngày/giờ nhập không hợp lệ.
        }
    }

    @JavascriptInterface
    public void cancelReminder(String id) {
        if (id == null || id.trim().isEmpty()) return;
        cancelAlarm(id);
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().remove(id).apply();
    }

    private void scheduleAt(String id, String title, long triggerAt) {
        Intent intent = new Intent(context, CareReminderReceiver.class);
        intent.setAction(ACTION);
        intent.putExtra("title", title);
        intent.putExtra("reminder_id", id);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(
                context, id.hashCode(), intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        AlarmManager manager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (manager != null) manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent);
    }

    private void cancelAlarm(String id) {
        Intent intent = new Intent(context, CareReminderReceiver.class);
        intent.setAction(ACTION);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(
                context, id.hashCode(), intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        AlarmManager manager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        if (manager != null) manager.cancel(pendingIntent);
        pendingIntent.cancel();
    }

    static void rescheduleAll(Context context) {
        SharedPreferences prefs = context.getApplicationContext()
                .getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        Map<String, ?> all = prefs.getAll();
        CareReminderBridge bridge = new CareReminderBridge(context);
        for (Map.Entry<String, ?> entry : all.entrySet()) {
            if (!(entry.getValue() instanceof String)) continue;
            String[] parts = ((String) entry.getValue()).split("\\n", -1);
            if (parts.length != 3) continue;
            try {
                SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US);
                format.setLenient(false);
                Date parsed = format.parse(parts[1] + " " + parts[2]);
                if (parsed == null || parsed.getTime() <= System.currentTimeMillis()) {
                    prefs.edit().remove(entry.getKey()).apply();
                    continue;
                }
                bridge.scheduleAt(entry.getKey(), parts[0], parsed.getTime());
            } catch (Exception ignored) {
                prefs.edit().remove(entry.getKey()).apply();
            }
        }
    }
}
