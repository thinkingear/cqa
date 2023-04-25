from django.db import models
from account.models import User
from core.models import Content, ContentFollower
from moviepy.editor import VideoFileClip
# Create your models here.


class Course(Content):
    title = models.CharField(max_length=128, default='')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
    description = models.TextField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    visibility = models.CharField(
        max_length=10,
        choices=[('private', 'Private'), ('public', 'Public')],
        default='private'
    )
    followers = models.ManyToManyField(User, through='CourseFollower', related_name='followed_courses')

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        # 删除关联的 thumbnail 图片文件
        if self.thumbnail:
            self.thumbnail.delete(save=False)

        for section in self.sections.all():
            section.delete()

        # 调用父类的 delete 方法，确保对象本身也被删除
        super(Course, self).delete(*args, **kwargs)

    @property
    def views(self):
        # 初始化 total_views 变量
        total_views = 0

        # 遍历每个 Section
        for section in self.sections.all():
            # 遍历每个 Video
            for video in section.videos.all():
                # 累加该视频的 views 到 total_views
                total_views += video.views

        # 返回总 views
        return total_views


class Section(models.Model):
    title = models.CharField(max_length=128)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    ordering = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        for video in self.videos.all():
            video.delete()

        super(Section, self).delete(*args, **kwargs)

    class Meta:
        ordering = ['ordering']


class Video(Content):
    title = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='videos')
    ordering = models.PositiveIntegerField(default=0)
    video_file = models.FileField(upload_to='videos/', null=True)
    views = models.PositiveIntegerField(default=0)
    followers = models.ManyToManyField(User, through='VideoFollower', related_name='followed_videos')
    review_status = models.CharField(
        max_length=10,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )

    class Meta:
        ordering = ['ordering']

    @property
    def get_duration(self):
        clip = VideoFileClip(self.video_file.path)
        duration = clip.duration
        clip.close()

        minutes, seconds = divmod(int(duration), 60)
        formatted_duration = f"{minutes:d}:{seconds:02d}"
        return formatted_duration

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        # 删除关联的 thumbnail 图片文件
        if self.video_file:
            self.video_file.delete(save=False)

        # 调用父类的 delete 方法，确保对象本身也被删除
        super(Video, self).delete(*args, **kwargs)


class CourseFollower(ContentFollower):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'course'], name='course_follower')
        ]


class VideoFollower(ContentFollower):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'video'], name='video_follower')
        ]


