from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse

from core.views import content_follow
from .models import Course, Section, Video
from .forms import CourseForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import re
from django.contrib.auth.decorators import login_required

# Create your views here.


def my_course(request):
    if request.method == 'GET':
        context = {}
        return render(request, 'course/my_course.html', context)


def course_detial(request, pk):
    course = Course.objects.get(id=pk)
    if request.method == 'GET':
        context = {'course': course}
        video_id = request.GET.get('video', '')
        if video_id == '':
            sections = course.sections.all()
            if len(sections) != 0:
                section = sections[0]
                videos = section.videos.all()
                if len(videos) != 0:
                    video_id = videos[0].id
                    url = reverse('course:course_detial', kwargs={'pk': course.id})
                    full_url = f"{url}?video={video_id}"
                    return redirect(full_url)
        else:
            video = Video.objects.get(id=video_id)
            context['video'] = video
        return render(request, 'course/course_detail.html', context)


@csrf_exempt
def course_delete(request, pk):
    course = Course.objects.get(id=pk)
    if request.method == 'DELETE':
        course.delete()
        return JsonResponse({'status': 'ok'})


@csrf_exempt
def course_follow(request):
    return content_follow(request, 'course', 'coursefollower')


@csrf_exempt
def video_follow(request):
    return content_follow(request, 'video', 'videofollower')


def new_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.poster = request.user
            course.save()

            # 匹配所有的 section 和 video
            section_title_pattern = re.compile(r'^sections\[\d+\].title$')
            section_video_title_pattern = re.compile(r'^sections\[\d+\].videos\[\d+\].title$')
            section_video_description_pattern = re.compile(r'^sections\[\d+\].videos\[\d+\].description$')
            section_video_file_pattern = re.compile(r'^sections\[\d+\].videos\[\d+\].file$')

            # 考虑到前端 section_counter 并非在自然数几何上连续
            # 故使用哈希表来记录前端 section_counter 到 section 实例的映射关系
            section_counter_2_section = {}
            for section_title_key, section_title_value in request.POST.items():
                if section_title_pattern.match(section_title_key):
                    counters = re.findall(r'\d+', section_title_key)
                    section_counter = int(counters[0])
                    section = Section.objects.create(
                        title=section_title_value,
                        course=course,
                        ordering=len(section_counter_2_section),
                    )
                    # 浅拷贝
                    section_counter_2_section[section_counter] = section
                    section.save()

            # 第一层映射：section_counter -> video_counter_2_video
            # 第二层映射：video_counter -> video
            section_counter_2_video_counter_2_video = {}
            for section_video_title_key, section_video_title_value in request.POST.items():
                if section_video_title_pattern.match(section_video_title_key):
                    counters = re.findall(r'\d+', section_video_title_key)
                    section_counter = int(counters[0])
                    video_counter = int(counters[1])

                    if section_counter not in section_counter_2_video_counter_2_video:
                        section_counter_2_video_counter_2_video[section_counter] = {}

                    section = section_counter_2_section[section_counter]

                    video = Video.objects.create(
                        poster=request.user,
                        title=section_video_title_value,
                        section=section,
                        ordering=len(section_counter_2_video_counter_2_video[section_counter])
                    )

                    section_counter_2_video_counter_2_video[section_counter][video_counter] = video

            for section_video_description_key, section_video_description_value in request.POST.items():
                if section_video_description_pattern.match(section_video_description_key):
                    counters = re.findall(r'\d+', section_video_description_key)
                    section_counter = int(counters[0])
                    video_counter = int(counters[1])
                    video = section_counter_2_video_counter_2_video[section_counter][video_counter]
                    video.description = section_video_description_value

            for section_video_file_key, section_video_file_value in request.FILES.items():
                if section_video_file_pattern.match(section_video_file_key):
                    counters = re.findall(r'\d+', section_video_file_key)
                    section_counter = int(counters[0])
                    video_counter = int(counters[1])
                    video = section_counter_2_video_counter_2_video[section_counter][video_counter]
                    video.video_file = section_video_file_value
                    video.save()

            return redirect('course:my_course')
        else:
            raise Http404("form data didn't valid")
    elif request.method == 'GET':
        form = CourseForm()
        context = {'form': form}
        return render(request, 'course/course_create.html', context)


@csrf_exempt
def update_course(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'GET':
        course_dict = model_to_dict(course)  # 将 course 对象转换为字典
        course_form = CourseForm(course_dict)  # 传递字典而不是 course 对象
        context = {'course': course, 'form': course_form}
        return render(request, 'course/course_update.html', context)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():

            course_new = form.save(commit=False)
            # update course's basic info
            course.title = course_new.title
            if course_new.thumbnail:
                course.thumbnail.delete()
                course.thumbnail = course_new.thumbnail

            course.description = course_new.description
            course.overview = course_new.overview
            course.visibility = course_new.visibility
            course.save()

            # update course's section
            # 匹配所有的 section 和 video
            section_title_pattern = re.compile(r'^sections\[\d+\].title$')
            section_id_pattern = re.compile(r'^sections\[\d+\].id$')
            section_video_title_pattern = re.compile(r'^sections\[\d+\].videos\[\d+\].title$')
            section_video_description_pattern = re.compile(r'^sections\[\d+\].videos\[\d+\].description$')
            section_video_file_pattern = re.compile(r'^sections\[\d+\].videos\[\d+\].file$')
            section_video_id_pattern = re.compile(r'^sections\[\d+\].videos\[\d+\].id$')
            # 考虑到前端 section_counter 并非在自然数几何上连续
            # 故使用哈希表来记录前端 section_counter 到 section 实例的映射关系
            # section_counter_2_object_id 的设置也是同理
            section_counter_2_section = {}
            section_counter_2_object_id = {}

            for section_id_key, section_id_value in request.POST.items():
                if section_id_pattern.match(section_id_key):
                    counters = re.findall(r'\d+', section_id_key)
                    section_counter = int(counters[0])
                    section_counter_2_object_id[section_counter] = int(section_id_value)

            # delete those sections whose id is not in the 'object_id_alive'
            object_id_alive = set(section_counter_2_object_id.values())
            for section in course.sections.all():
                if section.id not in object_id_alive:
                    section.delete()

            # update section title
            for section_title_key, section_title_value in request.POST.items():
                if section_title_pattern.match(section_title_key):
                    counters = re.findall(r'\d+', section_title_key)
                    section_counter = int(counters[0])
                    if section_counter in section_counter_2_object_id:
                        section = Section.objects.get(id=section_counter_2_object_id[section_counter])
                        section.title = section_title_value
                        section.ordering = len(section_counter_2_section)
                    else:
                        section = Section.objects.create(
                            title=section_title_value,
                            course=course,
                            ordering=len(section_counter_2_section),
                        )
                    section_counter_2_section[section_counter] = section
                    section.save()

            # 第一层映射：section_counter -> video_counter_2_video
            # 第二层映射：video_counter -> video
            section_counter_2_video_counter_2_video = {}
            # 第一层映射：section_counter -> video_counter_2_object_id
            # 第二层映射：video_counter_2_object_id -> id
            section_counter_2_video_counter_2_object_id = {}

            # collect ids which are still alive
            for section_video_id_key, section_video_id_value in request.POST.items():
                if section_video_id_pattern.match(section_video_id_key):
                    counters = re.findall(r'\d+', section_video_id_key)
                    section_counter = int(counters[0])
                    video_counter = int(counters[1])
                    if section_counter not in section_counter_2_video_counter_2_object_id:
                        section_counter_2_video_counter_2_object_id[section_counter] = {}

                    section_counter_2_video_counter_2_object_id[section_counter][video_counter] = int(section_video_id_value)

            # reverse the mapping direction
            section_object_id_2_counter = {}
            for key, value in section_counter_2_object_id.items():
                section_object_id_2_counter[value] = key

            # delete those videos whose id are not in set(section_counter_2_video_counter_2_object_id[section.id].values())
            for section in course.sections.all():
                # at this time, some totally new user added section could have been created in the course.sections,
                # so we have to exclude those sections first
                if section.id not in section_object_id_2_counter:
                    continue

                section_counter = section_object_id_2_counter[section.id]
                # considering that not id of section in database are already in the section_counter_2_video_counter_2_object_id
                # only those sections which remained in the course update page after the edition are in the section_counter_2_video_counter_2_object_id
                if section_counter not in section_counter_2_video_counter_2_object_id:
                    video_id_alive = set()
                else:
                    video_id_alive = set(section_counter_2_video_counter_2_object_id[section_counter].values())
                for video in section.videos.all():
                    if video.id not in video_id_alive:
                        video.delete()

            # update sectoin_video_title
            for section_video_title_key, section_video_title_value in request.POST.items():
                if section_video_title_pattern.match(section_video_title_key):
                    counters = re.findall(r'\d+', section_video_title_key)
                    section_counter = int(counters[0])
                    video_counter = int(counters[1])

                    if section_counter not in section_counter_2_video_counter_2_video:
                        section_counter_2_video_counter_2_video[section_counter] = {}

                    section = section_counter_2_section[section_counter]
                    if section_counter in section_counter_2_video_counter_2_object_id and video_counter in section_counter_2_video_counter_2_object_id[section_counter]:
                        video = Video.objects.get(id=section_counter_2_video_counter_2_object_id[section_counter][video_counter])
                        video.title = section_video_title_value
                        video.ordering = len(section_counter_2_video_counter_2_video[section_counter])
                    else:
                        video = Video.objects.create(
                            poster=request.user,
                            title=section_video_title_value,
                            section=section,
                            ordering=len(section_counter_2_video_counter_2_video[section_counter])
                        )

                    section_counter_2_video_counter_2_video[section_counter][video_counter] = video


            # update video description
            for section_video_description_key, section_video_description_value in request.POST.items():
                if section_video_description_pattern.match(section_video_description_key):
                    counters = re.findall(r'\d+', section_video_description_key)
                    section_counter = int(counters[0])
                    video_counter = int(counters[1])
                    video = section_counter_2_video_counter_2_video[section_counter][video_counter]
                    video.description = section_video_description_value

            # update video description
            for section_video_file_key, section_video_file_value in request.FILES.items():
                if section_video_file_pattern.match(section_video_file_key):
                    counters = re.findall(r'\d+', section_video_file_key)
                    section_counter = int(counters[0])
                    video_counter = int(counters[1])
                    video = section_counter_2_video_counter_2_video[section_counter][video_counter]

                    # if video.video_file are already lying in the filesystem, then we will delete it first
                    if video.video_file:
                        video.video_file.delete()
                    video.video_file = section_video_file_value

            # save videos
            for video_counter_2_video in section_counter_2_video_counter_2_video.values():
                for video in video_counter_2_video.values():
                    video.save()

            return redirect('course:my_course')
        else:
            return JsonResponse({'status': 'error'})


