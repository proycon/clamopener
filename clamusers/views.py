from django.shortcuts import render_to_response
from clamopener import settings
from clamopener.clamusers.forms import RegisterForm, pwhash
from clamopener.clamusers.models import CLAMUsers,PendingUsers
from django.http import HttpResponse, HttpResponseForbidden,HttpResponseNotFound
from django.core.mail import send_mail
from django.core.context_processors import csrf
from django.template import RequestContext
from django.db import IntegrityError
import hashlib

def autoactivate(clamuser):
    try:
        if '@' not in clamuser.mail:
            return False
        userdomain = clamuser.mail[clamuser.mail.find('@')+1:]
        for domain in settings.AUTOACTIVATE:
            if userdomain == domain or userdomain.endswith('.' + domain):
                return True
        return False
    except AttributeError:
        return False

def register(request):
    if request.method == 'POST': # If the form has been submitted...
        form = RegisterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                clamuser = form.save()
            except IntegrityError:
                return HttpResponseForbidden("That username is already registered (1)", content_type="text/plain")
            if autoactivate(clamuser):
                clamuser = CLAMUsers(username=clamuser.username, password=clamuser.password,fullname=clamuser.fullname, institution=clamuser.institution, mail=clamuser.mail,active=True)
                try:
                    clamuser.save()
                except IntegrityError:
                    return HttpResponseForbidden("That username is already registered (2)", content_type="text/plain")
                send_mail('[' + settings.DOMAIN + '] Registration request from ' + clamuser.username + ' automatically approved' , 'The following new account has been automatically approved, no further action is required:\n\nUsername: ' + clamuser.username + '\nFull name: '  +clamuser.fullname + '\nInstitution: ' + clamuser.institution + '\nMail: ' + clamuser.mail + '\n\n', settings.FROMMAIL, [ x[1] for x in settings.ADMINS ] , fail_silently=False)
                return render_to_response('activated.html')
            else:
                send_mail('[' + settings.DOMAIN + '] Registration request from ' + clamuser.username + ' pending approval' , 'The following new account is pending approval:\n\nUsername: ' + clamuser.username + '\nFull name: '  +clamuser.fullname + '\nInstitution: ' + clamuser.institution + '\nMail: ' + clamuser.mail + '\n\nTo approve this user go to: ' + settings.BASEURL + 'activate/' + str(clamuser.pk), settings.FROMMAIL, [ x[1] for x in settings.ADMINS ] , fail_silently=False)
                return render_to_response('submitted.html')
    else:
        c = RequestContext(request)
        c.update(csrf(request))
        form = RegisterForm() # An unbound form
        return render_to_response('register.html', {'form': form},context_instance=c)


def activate(request, userid):
    if request.method == 'POST':
        if hashlib.md5(request.POST['pw']).hexdigest() == settings.MASTER_PASSWORD:
            try:
                pendinguser = PendingUsers.objects.get(pk=int(userid))
            except:
                return HttpResponseNotFound("No such user", content_type="text/plain")
            clamuser = CLAMUsers(username=pendinguser.username, password=pendinguser.password,fullname=pendinguser.fullname, institution=pendinguser.institution, mail=pendinguser.mail,active=True)
            try:
                clamuser.save()
            except IntegrityError:
                return HttpResponseForbidden("User is already activated", content_type="text/plain")
            send_mail('Webservice account on ' + settings.DOMAIN , 'Dear ' + clamuser.fullname + '\n\nYour webservice account on ' + settings.DOMAIN + ' has been reviewed and activated.\n\n(this is an automated message)', settings.FROMMAIL, [clamuser.mail] + [ x[1] for x in settings.ADMINS ] , fail_silently=False)
            return HttpResponse("Succesfully activated", content_type="text/plain")
        else:
            return HttpResponseForbidden("Invalid password, not activated", content_type="text/plain")

    else:
        try:
            pendinguser = PendingUsers.objects.get(pk=int(userid))
        except:
            return HttpResponseNotFound("No such pending user, has probably already been activated", content_type="text/plain")

        c = RequestContext(request)
        c.update(csrf(request))
        return render_to_response('activate.html',{'userid': userid},context_instance=c)


def changepw(request, userid):
    if request.method == 'POST':
        try:
            clamuser = CLAMUsers.objects.get(pk=int(userid))
        except:
            return HttpResponseNotFound("No such user", content_type="text/plain")
        if ((pwhash(clamuser.username,request.POST['pw']) == clamuser.password) or (hashlib.md5(request.POST['pw']).hexdigest() == settings.MASTER_PASSWORD)):
            clamuser.password=pwhash(clamuser.username,request.POST['newpw'])
            clamuser.save()
            #send_mail('Webservice account on ' + settings.DOMAIN , 'Dear ' + clamuser.fullname + '\n\nYour webservice account on ' + settings.DOMAIN + ' has had its password changed to: ' + request.POST['newpw'] + ".\n\n(this is an automated message)", settings.FROMMAIL, [clamuser.mail] , fail_silently=False)
            return HttpResponse("Password changed", content_type="text/plain")
        else:
            return HttpResponseForbidden("Current password is invalid", content_type="text/plain")

    else:
        try:
            user = CLAMUsers.objects.get(pk=int(userid))
        except:
            return HttpResponseNotFound("No such user")

        c = RequestContext(request)
        c.update(csrf(request))
        return render_to_response('changepw.html',{'userid': userid},context_instance=c)



def userlist(request):
    if request.method == 'POST':
        if hashlib.md5(request.POST['pw']).hexdigest() != settings.MASTER_PASSWORD:
            return HttpResponseForbidden("Master password invalid", content_type="text/plain")
        c = RequestContext(request)
        c.update(csrf(request))
        return render_to_response('userlist_view.html',{'users': CLAMUsers.objects.filter(active=1)},context_instance=c)
    else:
        c = RequestContext(request)
        c.update(csrf(request))
        return render_to_response('userlist.html',context_instance=c)

def report(request):
    #s = "The following accounts are pending approval:\n\n"
    #report = []
    #for clamuser in PendingUsers.objects.filter(active=0):
    #    report.append('ID: ' + str(clamuser.pk) + '\nUsername: ' + clamuser.username + '\nFull name: '  +clamuser.fullname + '\nInstitution: ' + clamuser.institution + '\nMail: ' + clamuser.mail + '\n\nTo approve this user go to: ' + settings.BASEURL + 'activate/' + str(clamuser.pk)+'\n\n')

    #if report:
    #    s = "\n\n".join(report)
    #else:
    #    s = "(no pending accounts found)"

    #send_mail('[' + settings.DOMAIN + '] Report of pending accounts' , s , settings.FROMMAIL, [ x[1] for x in settings.ADMINS ] , fail_silently=False)

    return HttpResponse("not implemented")







